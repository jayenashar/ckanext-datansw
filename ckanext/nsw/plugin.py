import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

def related_create(context, data_dict=None):
    return {'success': False, 'msg': 'No one is allowed to create related items'}

class NSWPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IFacets, inherit=True)

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
