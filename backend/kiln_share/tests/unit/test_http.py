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
        headers1 = deepcopy(self.user1)
        r = self.post('auth/kilns', headers=headers1, data=kiln)
        self.assertEqual(r[1], 201)

        r = self.get('auth/kilns', headers=headers1)
        self.assertEqual(r[1], 200)

        result = r[0]
        self.assertEqual(result['_meta']['total'], 1)

        # Now with another user.
        headers2 = deepcopy(self.user2)
        r = self.get('auth/kilns', headers=headers2)
        self.assertEqual(r[1], 200)

        result = r[0]
        self.assertEqual(result['_meta']['total'], 0)

    def test_images(self):
        headers1 = deepcopy(self.user1)
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

        r = self.post('auth/kilns', headers=headers1, data=kiln)
        kiln_id = r[0]['_id']

        # Post an image.
        headers1 = deepcopy(self.user1)
        headers1.append(('Content-Type', 'multipart/form-data'))
        location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        file_ = open(os.path.join(location, 'img.jpg'));
        file_content = file_.read()
        data = {
            'file': (BytesIO(file_content), 'img.png'),
            'kiln': kiln_id
        }

        # Use test client directly to avoid json encoding.
        r = self.test_client.post('auth/images', data=data, headers=headers1)
        self.assertEqual(r.status_code, 201)

    def test_conversations_and_messages(self):
        headers1 = deepcopy(self.user1)
        headers2 = deepcopy(self.user2)
        headers3 = [('X-Kiln-Share-Id', 'baz')]

        # Check no data exists.
        for headers in [headers1, headers2, headers3]:
            r = self.get('auth/conversations', headers=headers)
            self.assertEqual(r[1], 200)
            result = r[0]
            self.assertEqual(result['_meta']['total'], 0)

        # Create a conversation.
        data = {
            'participants': ['bar']
        }
        r = self.post('auth/conversations', data=data, headers=headers1)
        self.assertEqual(r[1], 201)
        conversation_id = r[0]['_id']

        # Both users should see the conversation.
        for headers in [headers1, headers2]:
            r = self.get('auth/conversations', headers=headers)
            self.assertEqual(r[1], 200)
            result = r[0]
            self.assertEqual(result['_meta']['total'], 1)

        # But user 3 should not.
        r = self.get('auth/conversations', headers=headers3)
        self.assertEqual(r[1], 200)
        result = r[0]
        self.assertEqual(result['_meta']['total'], 0)

        # Now send a message.
        data = {
            'text': 'hello'
        }
        url = 'auth/conversations/%s/messages' % conversation_id
        r = self.post(url, data=data, headers=deepcopy(self.user1))
        self.assertEqual(r[1], 201)

        # User 3 shouldn't be able to post to the conversation.
        r = self.post(url, data=data, headers=headers3)
        self.assertEqual(r[1], 403)

        # Both users should see the message when fetching the
        # conversation.
        for headers in [headers1, headers2]:
            url = 'auth/conversations/%s' % conversation_id
            r = self.get(url, headers=headers)
            self.assertEqual(r[1], 200)
            result = r[0]
            self.assertEqual(len(result['messages']), 1)
