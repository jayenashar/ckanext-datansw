from functools import wraps
from ckan.lib.navl.validators import ignore_missing
from ckan.controllers.admin import AdminController
from ckan.common import config, _, c
import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckanext.acl.interfaces import IACL
from ckan.logic.action.get import user_list as ckan_user_list
import ckanext.nsw.helpers as helpers
import sqlalchemy

import ckan.lib.dictization.model_save as model_save
import ckan.logic.auth.create as create
import ckan.authz as authz
import ckan.logic as logic

_desc = sqlalchemy.desc


def nsw_check_group_auth(context, data_dict):
    if not data_dict:
        return True

    model = context['model']
    user = context['user']
    pkg = context.get("package")

    api_version = context.get('api_version') or '1'

    group_blobs = data_dict.get('groups', [])
    groups = set()
    for group_blob in group_blobs:
        # group_blob might be a dict or a group_ref
        if isinstance(group_blob, dict):
            # use group id by default, but we can accept name as well
            id = group_blob.get('id') or group_blob.get('name')
            if not id:
                continue
        else:
            id = group_blob
        grp = model.Group.get(id)
        if grp is None:
            raise logic.NotFound(_('Group was not found.'))
        groups.add(grp)

    if pkg:
        pkg_groups = pkg.get_groups()

        groups = groups - set(pkg_groups)
    groups = []
    for group in groups:
        if not authz.has_user_permission_for_group_or_org(
                group.id, user, 'manage_group'):
            return False

    return True

create._check_group_auth = nsw_check_group_auth


def nsw_package_membership_list_save(group_dicts, package, context):

    allow_partial_update = context.get("allow_partial_update", False)
    if group_dicts is None and allow_partial_update:
        return

    capacity = 'public'
    model = context["model"]
    session = context["session"]
    user = context.get('user')

    members = session.query(model.Member) \
        .filter(model.Member.table_id == package.id) \
        .filter(model.Member.capacity != 'organization')

    group_member = dict(
        (member.group, member)
        for member in
        members)
    groups = set()
    for group_dict in group_dicts or []:
        id = group_dict.get("id")
        name = group_dict.get("name")
        capacity = group_dict.get("capacity", "public")
        if capacity == 'organization':
            continue
        if id:
            group = session.query(model.Group).get(id)
        else:
            group = session.query(model.Group).filter_by(name=name).first()
        if group:
            groups.add(group)

    ## need to flush so we can get out the package id
    model.Session.flush()

    # Remove any groups we are no longer in
    for group in set(group_member.keys()) - groups:
        member_obj = group_member[group]
        if member_obj and member_obj.state == 'deleted':
            continue

        # Bypass authorization to enable datasets to be removed from AGIFT classification
        member_obj.capacity = capacity
        member_obj.state = 'deleted'
        session.add(member_obj)

    # Add any new groups
    for group in groups:
        member_obj = group_member.get(group)
        if member_obj and member_obj.state == 'active':
            continue

        # Bypass authorization to enable datasets to be added to AGIFT classification
        member_obj = group_member.get(group)
        if member_obj:
            member_obj.capacity = capacity
            member_obj.state = 'active'
        else:
            member_obj = model.Member(table_id=package.id,
                                      table_name='package',
                                      group=group,
                                      capacity=capacity,
                                      group_id=group.id,
                                      state='active')
        session.add(member_obj)

model_save.package_membership_list_save = nsw_package_membership_list_save


def related_create(context, data_dict=None):
    return {
        'success': False,
        'msg': 'No one is allowed to create related items'
    }


def nsw_user_list(context, data_dict):
    model = context['model']
    query = ckan_user_list(context, data_dict)
    query = query.order_by(None).order_by(_desc(model.User.created))
    return query


def _add_search_tooltip(original):
    @wraps(AdminController._get_config_form_items)
    def wrapper(*args, **kwargs):
        items = original(*args, **kwargs)
        items.append({
            'name': 'ckan.search_tooltip',
            'control': 'markdown',
            'label': _('Tooltip for search sorting'),
            'placeholder': _('Tooltip...')
        })
        return items
    return wrapper


AdminController._get_config_form_items = _add_search_tooltip(
    AdminController._get_config_form_items
)


class NSWPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(IACL)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config_schema(self, schema):
        schema['ckan.search_tooltip'] = [
            ignore_missing, unicode

        ]

        return schema

    def after_search(self, search_results, data_dict):
        if 'dctype' in search_results['facets']:
            count = 0
            for key in search_results['facets']['dctype']:
                count = count + search_results['facets']['dctype'][key]
            search_results['facets'][
                'dctype'
            ]['Dataset'] = search_results['facets']['dctype'].get(
                'Dataset', 0
            ) + (search_results['count'] - count)
            restructured_facet = {'title': 'dctype', 'items': []}
            for key_, value_ in search_results['facets']['dctype'].items():
                new_facet_dict = {}
                new_facet_dict['name'] = key_
                new_facet_dict['display_name'] = key_
                new_facet_dict['count'] = value_
                restructured_facet['items'].append(new_facet_dict)
            search_results['search_facets']['dctype'] = restructured_facet

        for result in search_results['results']:
            tracking = model.TrackingSummary.get_for_package(result['id'])
            result['tracking_summary'] = tracking

        return search_results

    def dataset_facets(self, facets, package_type):
        if 'dctype' in facets:
            facets['dctype'] = 'Type'
        return facets

    def get_auth_functions(self):
        return {'related_create': related_create}

    def before_map(self, map):
        map.connect(
            '/dataset/summary.csv',
            controller='ckanext.nsw.controller:NSWController',
            action='summarycsv'
        )
        map.connect(
            'format_mapping',
            '/ckan-admin/format-mapping',
            controller='ckanext.nsw.controller:NSWController',
            action='format_mapping',
            ckan_icon='arrows'
        )
        map.connect(
            'broken_links_report',
            '/ckan-admin/report/broken-links',
            controller='ckanext.nsw.controller:NSWController',
            action='broken_links',
            ckan_icon='link'
        )
        map.connect(
            'license_mapping',
            '/ckan-admin/license-mapping',
            controller='ckanext.nsw.controller:NSWController',
            action='license_mapping',
            ckan_icon='file-text'
        )
        return map

    def update_config(self, config):
        conf_directive = 'nsw.report.broken_links_filepath'
        if not config.get(conf_directive):
            raise KeyError(
                'Please, specify `{}` inside your config file'.
                format(conf_directive)
            )

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_template_directory(config, 'templates')

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_public_directory(config, 'public')

        # Add this plugin's fanstatic dir.
        tk.add_resource('fanstatic', 'ckanext-nsw')

        if tk.check_ckan_version(min_version='2.4'):
            tk.add_ckan_admin_tab(
                config, 'broken_links_report', 'Reports'
            )
            tk.add_ckan_admin_tab(
                config, 'format_mapping', 'Formats'
            )
            tk.add_ckan_admin_tab(
                config, 'license_mapping', 'Licenses'
            )

    # IACL

    def update_permission_list(self, perms):
        perms.create_permission('user_delete')

    # IActions

    def get_actions(self):
        return {'user_list': nsw_user_list}

    # ITemplateHelpers

    def get_helpers(self):
        return helpers.get_helpers()
