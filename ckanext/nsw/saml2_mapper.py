allowed_roles = set(['admin', 'editor', 'member'])


def nsw_org_mapper(saml_info):
    """Prepare org_dict using org=role[,role][|repeat] format."""
    tenancy = saml_info.get('tenancy', [])
    if tenancy:
        # remove None values before converting into dict.
        # None in that case means that role in organization is not determined
        org_dict = dict(filter(None, [
            _get_privileged_role(*part.split('='))
            for part in tenancy[0].split('|')
        ]))
        return org_dict


def _get_privileged_role(org, roles, separator=','):
    """Return tuple with organization and most privileged role."""
    # Roles sorted alphabetically. In order to change it, named
    # parameter :key can be used with function sorted
    capacity = sorted([
        role for role in roles.split(separator)
        if role in allowed_roles])
    # if role not in allowed list, None returned and mapper
    # should get rid of it
    if capacity:
        return org, dict(capacity=capacity.pop(0))
