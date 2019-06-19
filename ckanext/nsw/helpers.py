import json

import ckan.model as model
from ckan.common import c

from ckanext.nsw.model.nsw_likes import EntityLikes


def get_helpers():
    return {
        'external_license_label': external_license_label,
        'check_liked': check_liked,
        'get_liked_count': get_liked_count
    }


def external_license_label(items):
    mapped_licenses = model.get_system_info('mapped_licenses')
    if mapped_licenses:
        mapped_licenses = json.loads(mapped_licenses)
        for item in items:
            if item['name'] in mapped_licenses:
                item['display_name'] = mapped_licenses[item['name']]
    return items


def check_liked(id):
    # c.author is an old property need to clarify with CKAN team
    if not c.user:
        user = c.author
    else:
        user = model.User.get(c.user)
        if user:
            user = user.id
    if user:
        q = model.Session.query(EntityLikes) \
            .filter(EntityLikes.entity_id == id) \
            .filter(EntityLikes.user == user) \
            .first()
        if q:
            return q
        else:
            return None
    return None


def get_liked_count(id):
    count = model.Session.query(EntityLikes) \
        .filter(EntityLikes.entity_id == id).count()
    return count
