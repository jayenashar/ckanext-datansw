from ckan.common import response
from ckan.controllers.package import PackageController
import ckan.logic as logic
import ckan.plugins.toolkit as tk

import ckan.lib.base as base

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
import cStringIO

import csv


class NSWController(PackageController):
    def summarycsv(self, html=False):
        import ckan.model as model

        output = cStringIO.StringIO()
        csvwriter = csv.writer(output)
        header = ['Title', 'Description', 'Organisation', 'Licence', 'Resource Name', 'Resource Description', 'Resource URL']
        csvwriter.writerow(header)
        response.headers['Content-Type'] = 'application/octet-stream; charset=utf-8'
        response.headers["Content-Disposition"] = "attachment; filename=summary.csv"

        context = {'model': model}


        for pkg_dict in logic.get_action('package_search')(context,{'fq':'-harvest_portal:*','rows':9999})['results']:
            try:
                row = []
                row.append(pkg_dict['title'].encode('ascii', 'ignore'))
                row.append(pkg_dict['notes'].encode('ascii', 'ignore') if 'notes' in pkg_dict and pkg_dict['notes'] != None else ' ')
                row.append(pkg_dict['organization']['title'].encode('ascii',
                                                                            'ignore') \
                                    if 'organization' in pkg_dict and pkg_dict['organization'] != None else ' ')
                row.append(pkg_dict['license_title'].encode('ascii', 'ignore') if 'license_title' in pkg_dict and pkg_dict['license_title'] != None else ' ')
                for resource in pkg_dict['resources']:
                    res_list = []
                    res_list.append(resource['name'].encode('ascii', 'ignore')
                                    if 'name' in resource and resource['name'] != None else '')
                    res_list.append(
                        resource['description'].encode('ascii', 'ignore')
                                    if 'description' in resource and resource['description'] != None else '')
                    res_list.append(
                        resource['url'].encode('ascii', 'ignore') if 'url' in resource and resource['url'] != None else '')
                    csvwriter.writerow(row + res_list)
            except NotAuthorized:
                pass

        return output.getvalue()
