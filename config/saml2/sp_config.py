import os.path

from saml2 import BINDING_HTTP_REDIRECT
from saml2.saml import NAME_FORMAT_URI

BASE= 'https://data.nsw.gov.au/data/'
CONFIG_PATH = '/etc/ckan/nsw/saml2'

CONFIG = {
    'entityid' : BASE + 'saml2/sp',
    'description': 'CKAN saml2 authorizor',
    'service': {
        'sp': {
            'name' : 'CKAN SP',
            'endpoints': {
                'assertion_consumer_service': [BASE + 'saml2/sso'],
                'single_logout_service' : [(BASE + 'saml2/slo',
                                            BINDING_HTTP_REDIRECT)],
            },
            'required_attributes': [
                'uid',
                'name',
                'mail',
                'status',
                'roles',
                'field_display_name',
                'realname',
                'field_unique_id',
                'field_type_of_user',
                'field_organization_type',
                'field_agency',
                'field_organization',
            ],
            'name_id_format': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
            'allow_unsolicited': True,
            'optional_attributes': [],
            'idp': ['https://portal.identityhub.nsw.gov.au/oamfed'],
            'subject_data': ['memcached', 'http://db.fnsw.links.com.au:11211'],
        }
    },
    'debug': 0,
    'key_file': CONFIG_PATH + '/pki/key.pem',
    'cert_file': CONFIG_PATH + '/pki/cert.pem',
    'attribute_map_dir': CONFIG_PATH + '/attributemaps',
    'metadata': {
       'local': [CONFIG_PATH + '/idhub-idp-edited.xml'],
    },
    # -- below used by make_metadata --
    'organization': {
        'name': 'Data.NSW',
        'display_name': [('Data.NSW','en')],
        'url':'https://data.nsw.gov.au',
    },
    'contact_person': [{
        'email_address': ['support@linkdigital.com.au'],
        'contact_type': 'technical',
        },
    ],
    'name_form': NAME_FORMAT_URI,
    'logger': {
        'rotating': {
            'filename': '/var/log/ckan-saml2/default.sp.log',
            'maxBytes': 100000,
            'backupCount': 5,
            },
        'loglevel': 'info',
    }
}
