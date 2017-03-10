import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckanext.acl.interfaces import IACL

def related_create(context, data_dict=None):
    return {'success': False, 'msg': 'No one is allowed to create related items'}

class NSWPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(IACL)

    def after_search(self, search_results, data_dict):
        if 'dctype' in search_results['facets']:
            count = 0
            for key in search_results['facets']['dctype']:
                count = count + search_results['facets']['dctype'][key]
            search_results['facets']['dctype']['Dataset'] = search_results['facets']['dctype'].get('Dataset',0) + (search_results['count'] - count)
            restructured_facet = {
                'title': 'dctype',
                'items': []
            }
            for key_, value_ in search_results['facets']['dctype'].items():
                new_facet_dict = {}
                new_facet_dict['name'] = key_
                new_facet_dict['display_name'] = key_
                new_facet_dict['count'] = value_
                restructured_facet['items'].append(new_facet_dict)
            search_results['search_facets']['dctype'] = restructured_facet
        return search_results

    def dataset_facets(self, facets, package_type):
        if 'dctype' in facets:
            facets['dctype'] = 'Type'
        return facets

    def get_auth_functions(self):
        return {'related_create': related_create}
    def before_map(self, map):
        map.connect('/summary.csv',
                    controller='ckanext.nsw.controller:NSWController', action='summarycsv')
        return map

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_template_directory(config, 'templates')

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_public_directory(config, 'public')

        # Add this plugin's fanstatic dir.
        tk.add_resource('fanstatic', 'ckanext-nsw')

    # IACL

    def update_permission_list(self, perms):
        perms.create_permission('user_delete')
