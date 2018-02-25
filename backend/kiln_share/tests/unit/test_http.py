import json
import os

from copy import deepcopy
from eve.tests import TestMinimal
from flask_pymongo import MongoClient
from io import BytesIO

import kiln_share

from kiln_share.settings import MONGO_HOST, MONGO_PORT, MONGO_DBNAME


class TestKilnShare(TestMinimal):

    def setUp(self):
        self.this_directory = os.path.dirname(os.path.realpath(__file__))
        self.settings_file = os.path.join(self.this_directory,
                                     '../../settings.py')
        self.connection = None
        self.setupDB()
        self.app = kiln_share.create_app()
        self.test_client = self.app.test_client()
        self.domain = self.app.config['DOMAIN']

        # Setup some common test users.
        self.user1 = [('X-Kiln-Share-Id', 'foo')]
        self.user2 = [('X-Kiln-Share-Id', 'bar')]

    def setupDB(self):
        self.connection = MongoClient(MONGO_HOST, MONGO_PORT)
        self.connection.drop_database(MONGO_DBNAME)

    def dropDB(self):
        self.connection = MongoClient(MONGO_HOST, MONGO_PORT)
        self.connection.drop_database(MONGO_DBNAME)
        self.connection.close()

    def get(self, url, headers=None, content_type='application/json'):
        if headers is None:
            headers = []
        headers.append(('Content-Type', content_type))
        r = self.test_client.get(url, headers=headers)
        return self.parse_response(r)

    def test_multi_tenancy(self):
        kiln = {
            'name': 'Test kiln',
            'share_type': 'any',
            'location': {
                'type': 'Point',
                'coordinates': [ 10.321, 5.123 ]
            },
            'power': 'electric',
            'chamber_size': 100,
            'max_temperature': 1000,
            'cost_per_fire': 10.50,
            'description': 'foo bar'
        }
        r = self.post('auth/kilns', headers=self.user1, data=kiln)
        self.assertEqual(r[1], 201)

        r = self.get('auth/kilns', headers=self.user1)
        self.assertEqual(r[1], 200)

        result = r[0]
        self.assertEqual(result['_meta']['total'], 1)

        # Now with another user.
        r = self.get('auth/kilns', headers=self.user2)
        self.assertEqual(r[1], 200)

        result = r[0]
        self.assertEqual(result['_meta']['total'], 0)

    def test_images(self):
        headers = deepcopy(self.user1)
        kiln = {
            'name': 'Test kiln',
            'share_type': 'any',
            'location': {
                'type': 'Point',
                'coordinates': [ 10.321, 5.123 ]
            },
            'power': 'electric',
            'chamber_size': 100,
            'max_temperature': 1000,
            'cost_per_fire': 10.50,
            'description': 'foo bar'
        }

        r = self.post('auth/kilns', headers=headers, data=kiln)
        kiln_id = r[0]['_id']

        # Post an image.
        headers = deepcopy(self.user1)
        headers.append(('Content-Type', 'multipart/form-data'))
        location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        file_ = open(os.path.join(location, 'img.jpg'));
        file_content = file_.read()
        data = {
            'file': (BytesIO(file_content), 'img.png'),
            'kiln': kiln_id
        }

        # Use test client directly to avoid json encoding.
        r = self.test_client.post('auth/images', data=data, headers=headers)
        self.assertEqual(r.status_code, 201)
