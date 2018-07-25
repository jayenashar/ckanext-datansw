import cStringIO
import csv
import os

from datetime import datetime
from operator import methodcaller

from sqlalchemy import func

from ckan.lib.search import rebuild, commit, clear
import ckan.model as model
import ckan.plugins.toolkit as tk
import ckan.logic as logic
import ckan.lib.helpers as h
from ckan.common import response, request, config, g
from ckan.controllers.package import PackageController

ascii = methodcaller('encode', 'ascii', 'ignore')


def set_attachment(response, filename):
    response.headers["Content-Disposition"
                     ] = "attachment; filename=" + filename


def get_key(self, container, key, default=''):
    return container.get(key) or default


class NSWController(PackageController):
    def format_mapping(self):
        try:
            tk.check_access('sysadmin', {'user': g.user, model: model})
        except tk.NotAuthorized:
            return tk.abort(403)
        if request.method == 'POST':
            old = request.POST.get('from')
            new = request.POST.get('to')
            if old and new:
                ids = set()
                res_query = model.Session.query(model.Resource).filter_by(
                    format=old, state='active'
                )
                for res in res_query:
                    ids.add(res.package_id)

                res_query.update({'format': new})
                model.Session.commit()
                for id in ids:
                    clear(id)
                    rebuild(id, defer_commit=True)
                commit()
                tk.h.flash_success(
                    'Updated. Records changed: {}'.format(len(ids))
                )
            return tk.redirect_to('format_mapping')

        defined = set(
            map(lambda (_1, fmt, _3): fmt,
                h.resource_formats().values())
        )
        db_formats = model.Session.query(
            model.Resource.format, func.count(model.Resource.id),
            func.count(model.PackageExtra.value)
        ).outerjoin(
            model.PackageExtra,
            (model.Resource.package_id == model.PackageExtra.package_id)
            & ((model.PackageExtra.key == 'harvest_portal')
               | (model.PackageExtra.key.is_(None)))
        ).group_by(model.Resource.format).filter(
            model.Resource.format != '', model.Resource.state == 'active'
        )
        db_formats = db_formats.all()

        format_types = {
            f: {
                True: 'Partially external',
                e == 0: 'Local',
                t - e == 0: 'External'
            }[True]
            for (f, t, e) in db_formats
        }
        used = set(format_types)
        undefined = used - defined

        extra_vars = {
            'undefined': undefined,
            'defined': defined,
            'format_types': format_types
        }
        return tk.render('admin/format_mapping.html', extra_vars)

    def broken_links(self):
        try:
            tk.check_access('sysadmin', {'user': g.user, model: model})
        except tk.NotAuthorized:
            return tk.abort(403)
        filepath = config['nsw.report.broken_links_filepath']
        try:
            last_check = datetime.fromtimestamp(os.stat(filepath).st_mtime)
        except OSError:
            last_check = None
        if request.method == 'POST' and last_check:
            set_attachment(
                response,
                'DataNSW-BrokenLinks-{:%Y-%m-%d}.csv'.format(last_check)
            )
            return open(filepath).read()
        extra_vars = {'last_check': last_check}
        return tk.render('admin/broken_links.html', extra_vars)

    def summarycsv(self, html=False):
        import ckan.model as model
        set_attachment(response, 'summary.csv')
        output = cStringIO.StringIO()
        csvwriter = csv.writer(output)

        csvwriter.writerow([
            'Title', 'Description', 'Organisation', 'Licence', 'Resource Name',
            'Resource Description', 'Resource URL'
        ])

        data = logic.get_action('package_search')({
            'model': model
        }, {
            'fq': '-harvest_portal:*',
            'rows': 9999
        })
        for pkg_dict in data['results']:
            row = []
            row.append(ascii(pkg_dict['title']))
            row.append(ascii(get_key(pkg_dict, 'notes')))
            row.append(
                ascii(get_key(pkg_dict.get('organization', {}), 'title'))
            )
            row.append(ascii(get_key(pkg_dict, 'license_title')))
            for resource in pkg_dict['resources']:
                res_list = []
                for key in ('name', 'description', 'url'):
                    res_list.append(ascii(get_key(resource, key)))
                csvwriter.writerow(row + res_list)

        return output.getvalue()
