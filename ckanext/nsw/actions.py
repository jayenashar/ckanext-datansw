import uuid
import datetime

import ckan.model as model
import ckan.logic as logic
import ckan.lib.helpers as h
from ckan.common import c
from ckan.authz import (
	auth_is_anon_user
	)

from ckanext.nsw.model.nsw_likes import EntityLikes
import ckanext.nsw.helpers as nsw_helper


def get_actions():
    return {
        'handle_likes': handle_likes,
    }

def handle_likes(context, data_dict):
	# c.author is an old property need to clarify with CKAN team
	if not c.user:
		user = c.author
	else:
		user = model.User.get(c.user)
		if user:
			user = user.id

	entity_id = data_dict.get('entity_id')
	entity_name = data_dict.get('entity_name')
	entity_type = data_dict.get('entity_type')
	liked = nsw_helper.check_liked(entity_id)
	liked_flag = False

	if user:
		if liked:
			model.Session.query(EntityLikes)\
				.filter(EntityLikes.entity_id == entity_id)\
				.filter(EntityLikes.user == user).delete()
		else:
			id = str(uuid.uuid4())
			data = {
				'id': id,
				'user': user,
				'entity_id': entity_id,
				'entity_name': entity_name,
				'entity_type': entity_type,
			}
			dt = EntityLikes(**data)
			model.Session.add(dt)
			liked_flag = True

		model.Session.commit()

		count = nsw_helper.get_liked_count(entity_id)

		return {
			'success': True,
			'liked_flag': liked_flag,
			'count': count}
	return {'success': False}