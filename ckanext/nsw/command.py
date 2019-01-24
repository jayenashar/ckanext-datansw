# -*- coding: utf-8 -*-
import logging
import csv
import paste.script
from ckan.plugins import toolkit
import tempfile
import requests
import sys

from io import StringIO

import ckan.model as model
from ckan.lib.cli import CkanCommand
import ckan.lib.helpers as h
from ckan.common import config
import requests.exceptions as exc

log = logging.getLogger(__name__)


class NSWCommand(CkanCommand):
    """
    Ckanext-nsw management commands.

    Usage::
        paster nsw [command]

    Commands::
        dropuser <name> - completely removes user from DB if he does not have any meaningful relationship with data.
	drop-oeh <name or id> - purges OEH datasets
        maintainer-report
    """

    summary = __doc__.split('\n')[0]
    usage = __doc__

    parser = paste.script.command.Command.standard_parser(verbose=True)
    parser.add_option(
        '-c',
        '--config',
        dest='config',
        default='development.ini',
        help='Config file to use.'
    )

    def command(self):
        self._load_config()
        if len(self.args) < 1:
            print self.usage
        elif self.args[0] == 'dropuser':
            self._drop_user(self.args[1])
        elif self.args[0] == 'drop-oeh':
            self._drop_oeh()
        elif self.args[0] == 'maintainer-report':
            self._maintainer_report()
        elif self.args[0] == 'broken-links-report':
            self._broken_links_report()
        elif self.args[0] == 'sso-user-reset-notification':
            self._sso_user_reset_notification()
        else:
            print self.usage

    def _drop_user(self, username):
        user = model.User.get(username)
        if user is None:
            print('User <%s> not found' % username)
            return
        groups = user.get_groups()
        if groups:
            print(
                'User is a member of groups/organizations: %s' %
                ', '.join([g.title or g.name for g in groups])
            )
            return
        pkgs = model.Session.query(model.Package
                                   ).filter_by(creator_user_id=user.id)
        if pkgs.count():
            print(
                'There are some(%d) datasets created by this user: %s' %
                (pkgs.count(), [pkg.name for pkg in pkgs])
            )
            return
        activities = model.Session.query(
            model.Activity
        ).filter_by(user_id=user.id).filter(
            model.Activity.activity_type.contains('package')
        )
        if activities.count():
            print(
                'There are some(%d) activity records that mentions user' %
                activities.count()
            )
            return
        model.Session.delete(user)
        model.Session.commit()
        print('Done')


    def _drop_oeh(self):
        def _drop_datasets(q):
            packages = toolkit.get_action('package_search')(None, {
                'fq': q,
                'rows': 100
            })
            i = 0
            for i, dataset in enumerate(packages['results'], 1):
                print('[{}/{}] Purge {}'.format(i + removed_count, total,
                                                dataset['name']))
                pkg = model.Package.get(dataset['id'])
                try:
                    model.Session.query(model.PackageExtraRevision).filter_by(
                        package_id=dataset['id']).delete()
                    model.Session.query(model.PackageExtra).filter_by(
                        package_id=dataset['id']).delete()
                    pkg.purge()
                    model.Session.commit()
                except Exception as e:
                    print('\tError: {}'.format(e))
                else:
                    print('\tSuccess')
            return i

        id_ = None
        if len(self.args) > 1:
            id_ = self.args[1]
        q = 'organization:office-of-environment-and-heritage-oeh'
        if id_:
            q += ' AND (id:{0} OR name:{0})'.format(id_)
        packages = toolkit.get_action('package_search')(None, {
            'fq': q,
            'rows': 0
        })
        total = packages['count']
        removed_count = 0
        print('Found {} datasets. Purging...'.format(total))

        while True:
            if removed_count:
                print(
                    'Already removed {} datasets. Fetching next portion'.
                    format(removed_count))
            removed_count += _drop_datasets(q)
            if removed_count >= total:
                break
        print('Done')

    def _maintainer_report(self):
        q = model.Session.query(model.Package)
        output = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        writer = csv.writer(output)

        writer.writerow(['Title', 'URL', 'Maintainer email'])
        for pkg in q:
            if pkg.extras.get('harvest_url'):
                continue
            writer.writerow([pkg.title.encode('utf8'), h.url_for('dataset_read', id=pkg.name, qualified=True), pkg.maintainer_email])

        print('Report: {}'.format(output.name))

    def _broken_links_report(self):
        broken_count = 0
        resources = model.Session.query(model.Resource
                                        ).filter_by(state='active')
        total = resources.count()
        file = open(config['nsw.report.broken_links_filepath'], 'wb')
        report = csv.writer(file)
        report.writerow(['Page', 'Broken URL', 'HTTP Code', 'Reason'])
        for i, res in enumerate(resources, 1):
            print '\rProcessing {} of {}. Broken links: {}'.format(
                i, total, broken_count
            ),
            sys.stdout.flush()
            page = h.url_for(
                controller='package',
                action='resource_read',
                id=res.package_id,
                resource_id=res.id,
                qualified=True
            )
            try:
                resp = requests.head(res.url, timeout=5)
                if resp.ok:
                    continue
                code, reason = resp.status_code, resp.reason
            except (exc.ConnectTimeout, exc.ReadTimeout):
                code, reason = 504, 'Request timeout'
            except exc.ConnectionError:
                code, reason = 520, 'Connection Error'
            except (exc.MissingSchema, exc.InvalidSchema):
                continue
            except exc.InvalidURL:
                code, reason = 520, 'Invalid URL'

            report.writerow([page, res.url, code, reason])
            broken_count += 1
        file.close()

    def _sso_user_reset_notification(self):
        import ckan.lib.mailer as mailer
        from ckanext.saml2.model.saml2_user import SAML2User
        saml2_users = model.Session.query(SAML2User.id).all()
        if len(self.args) > 1:
            users = model.Session.query(model.User)\
               .filter(model.User.name == self.args[1])\
               .filter(model.User.id.in_(saml2_users)).limit(1).all()
        else:
            users = model.Session.query(model.User)\
                .filter(model.User.id.in_(saml2_users))\
                .all()
        for user in users:
            if user:
                print('*' * 100)
                mailer.create_reset_key(user)
                reset_link = mailer.get_reset_link(user)
                subject = 'Data.NSW & IAR ID Hub decommissioning'
                msg = ('Dear {0},\n\n'

                'We need to change the login process for Data NSW. On 6 February 2019, the NSW Identity Hub service will no longer be available as an identity provider for Data NSW. We therefore need to transition to a CKAN-based login process.\n\n'

                'In order to maintain your access to Data NSW and the Information Access Register, you will need to reset your password to login to Data NSW.\n\n'

                'To reset your password, as soon as possible please visit: {1} \n\n'

                'Once your password is reset, you will be able to use this new password and the login functionality on the Data NSW homepage to access your datasets. Please note, your Data NSW user name is used in the salutation of this message.\n\n'

                'From 6 February you will no longer be able to use the NSW Identity Hub to access Data NSW.\n\n'

                'If you have any questions or concerns about these changes, please contact the Information and Data Policy team at the Department of Finance, Services and Innovation at datansw@finance.nsw.gov.au\n\n'

                'Kind Regards,\n'
                'The Data NSW team\n'
                'Department Finance, Services and Innovation').format(user.name, reset_link)
                if user.email:
                    mailer.mail_recipient(user.name, user.email, subject, msg)
                    log.info("User pass reset email should be sent to {0} user.".format(user.name))
                    print("User pass reset email should be sent to {0} user.".format(user.name))
                else:
                    log.error("User {0} don't have email".format(user.name))
                    print("User {0} don't have email".format(user.name))
                print('*' * 100)
