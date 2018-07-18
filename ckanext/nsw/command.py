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
            except exc.ConnectTimeout:
                code, reason = 504, 'Request timeout'
            except exc.ConnectionError:
                code, reason = 520, 'Connection Error'
            report.writerow([page, res.url, code, reason])
            broken_count += 1
        file.close()
