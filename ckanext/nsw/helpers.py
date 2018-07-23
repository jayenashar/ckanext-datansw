import json

import ckan.model as model


def get_helpers():
    return {
        'external_license_label': external_license_label
    }


def external_license_label(items):
    mapped_licenses = model.get_system_info('mapped_licenses')
    mapped_licenses = json.loads(mapped_licenses)
    for item in items:
        if item['name'] in mapped_licenses:
            item['display_name'] = mapped_licenses[item['name']]
    return items
