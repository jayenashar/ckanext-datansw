# -*- coding: utf-8 -*-
import logging

import paste.script

import ckan.model as model
from ckan.lib.cli import CkanCommand


log = logging.getLogger(__name__)

class NSWCommand(CkanCommand):
    """
    Ckanext-nsw management commands.

    Usage::
        paster nsw [command]

    Commands::
        dropuser <name> - completely removes user from DB if he does not have any meaningful relationship with data.
    """

    summary = __doc__.split('\n')[0]
    usage = __doc__

    parser = paste.script.command.Command.standard_parser(verbose=True)
    parser.add_option('-c', '--config', dest='config',
                      default='development.ini',
                      help='Config file to use.')

    def command(self):
        self._load_config()
        if len(self.args) < 2:
            print self.usage
        elif self.args[0] == 'dropuser':
            self._drop_user(self.args[1])
        else:
            print self.usage

    def _drop_user(self, username):
        user = model.User.get(username)
        if user is None:
            print('User <%s> not found' % username)
            return
        groups = user.get_groups()
        if groups:
            print('User is a member of groups/organizations: %s' % ', '.join(
                [g.title or g.name for g in groups]
            ))
            return
        pkgs = model.Session.query(model.Package).filter_by(
            creator_user_id=user.id)
        if pkgs.count():
            print('There are some(%d) datasets created by this user: %s'
                  % (pkgs.count(), [pkg.name for pkg in pkgs]))
            return
        activities = model.Session.query(model.Activity).filter_by(
            user_id=user.id
        ).filter(model.Activity.activity_type.contains('package'))
        if activities.count():
            print('There are some(%d) activity records that mentions user'
                  % activities.count())
            return
        model.Session.delete(user)
        model.Session.commit()
        print('Done')
