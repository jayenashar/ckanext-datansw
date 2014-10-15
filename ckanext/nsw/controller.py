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
        header = ['Title', 'Description', 'Publisher', 'Resource Name', 'Resource Description', 'Resource URL']
        csvwriter.writerow(header)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers["Content-Disposition"] = "attachment; filename=summary.csv"

        context = {'model': model}

        model = context['model']

        query = model.Session.query(model.Package)

        for pkg in query.all():
            try:
                pkg_dict = tk.get_action("package_show")(context, {"id": pkg.id})
                row = {}
                row['Title'] = pkg_dict['title'].encode('ascii', 'ignore')
                row['Description'] = pkg_dict['notes'].encode('ascii', 'ignore')
                row['Publisher'] = pkg_dict['organization']['title'].encode('ascii',
                                                                            'ignore') \
                                    if 'organization' in pkg_dict and pkg_dict['organization'] != None else ''
                for resource in pkg_dict['resources']:
                    res_list = []
                    res_list.append(resource['name'].encode('ascii', 'ignore')
                                    if 'name' in resource and resource['name'] != None else '')
                    res_list.append(
                        resource['description'].encode('ascii', 'ignore')
                                    if 'description' in resource and resource['description'] != None else '')
                    res_list.append(
                        resource['url'].encode('ascii', 'ignore') if 'url' in resource and resource['url'] != None else '')
                    csvwriter.writerow(row.values() + res_list)
            except NotAuthorized:
                pass

        return output.getvalue()
