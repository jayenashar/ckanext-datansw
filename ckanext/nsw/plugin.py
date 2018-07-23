from functools import wraps
from ckan.lib.navl.validators import ignore_missing
from ckan.controllers.admin import AdminController
from ckan.common import config, _, c
import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckanext.acl.interfaces import IACL
from ckan.logic.action.get import user_list as ckan_user_list
import sqlalchemy

import ckanext.nsw.helpers as helpers

_desc = sqlalchemy.desc


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
