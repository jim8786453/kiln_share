# -*- coding: utf-8 -*-

import os

from kiln_share import logs


# Create a logger
logger = logs.get_logger(__name__)


# Eve Database settings
MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.environ.get('MONGO_PORT', 27017))
MONGO_USERNAME = os.environ.get('MONGO_USERNAME', '')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', '')
MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'kiln_share')
MONGO_QUERY_BLACKLIST = ['$where']


# Eve cache settings
CACHE_CONTROL = 'no-cache'
CACHE_EXPIRES = 0


# Eve general settings
AUTH_FIELD = "auth0_id"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
ITEM_METHODS = []
PAGINATION_DEFAULT = 10
RESOURCE_METHODS = []
VERSIONING = True
XML = False
X_DOMAINS = ['*']
X_HEADERS = ['Content-type', 'If-Match']


# Eve change logging
OPLOG = True
OPLOG_ENDPOINT = 'history'
OPLOG_RETURN_EXTRA_FIELD = True


# Eve media and image settings
EXTENDED_MEDIA_INFO = ['content_type', 'name', 'length']
MEDIA_ENDPOINT = 'media'
RETURN_MEDIA_AS_BASE64_STRING = False
RETURN_MEDIA_AS_URL = True


# Schema
DOMAIN = {
    'kilns': {
        'url': 'auth/kilns',
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'DELETE'],
        'item_title': 'Kilns',
        'description': 'Kilns to share',
        'mongo_indexes': {
            'index name': [('location', '2dsphere')],
        },
        'schema': {
            'name': {
                'type': 'string',
                'required': True,
            },
            'type': {
                'type': 'string',
                'required': True,
                'allowed': [
                    'solo',
                    'colo',
                    'firing_only',
                    'any'
                ],
                'default': 'any'
            },
            'location': {
                'type': 'point',
                'required': False,
            },
            'power': {
                'type': 'string',
                'allowed': [
                    'electric',
                    'gas',
                    'other'
                ],
                'default': 'electric',
                'required': True
            },
            'other_type': {
                'type': 'string',
                'required': False
            },
            'chamber_size': {
                'type': 'number',
                'required': False
            },
            'max_temperature': {
                'type': 'number',
                'required': False
            },
            'cost_per_fire': {
                'type': 'number',
                'required': True
            },
            'description': {
                'type': 'string',
                'required': False
            }
        }
    },
    'images': {
        'url': 'auth/kilns/<regex("(?s).*"):kiln>/images',
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'DELETE'],
        'item_title': 'Images',
        'description': 'Images of kilns',
        'schema': {
            'kiln': {
                'type': 'objectid',
                'required': True,
                'data_relation': {
                    'resource': 'kilns',
                    'embeddable': True
                },
            },
            'file': {
                'type': 'media',
                'required': True
            }
        }
    }
}
