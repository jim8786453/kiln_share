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

        # Setup some common test data.
        user = {
            'auth0_id': 'foo'
        }
        r = self.post('api/users', data=user)
        self.assertEqual(r[1], 201)

    def setupDB(self):
        self.connection = MongoClient(MONGO_HOST, MONGO_PORT)
        self.connection.drop_database(MONGO_DBNAME)

    def dropDB(self):
        self.connection = MongoClient(MONGO_HOST, MONGO_PORT)
        self.connection.drop_database(MONGO_DBNAME)
        self.connection.close()

    def test_swagger(self):
        r = self.get('api-docs')
        self.assertEqual(r[1], 200)

    def test_users(self):
        r = self.post('api/users', data={})
        self.assertEqual(r[1], 422)

        user = {
            'auth0_id': 'foo'
        }
        r = self.post('api/users', data=user)
        self.assertEqual(r[1], 422)

        user = {
            'auth0_id': 'bar'
        }
        r = self.post('api/users', data=user)
        self.assertEqual(r[1], 201)

        r = self.get('api/users')
        assert len(r[0]['_items']) == 2

    def test_kilns(self):
        r = self.get('api/users')
        user = r[0]['_items'][0]

        kiln = {
            'name': 'Test kiln',
            'user': user['_id'],
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
        r = self.post('api/kilns', data=kiln)
        self.assertEqual(r[1], 201)

    def test_images(self):
        r = self.get('api/users')
        user = r[0]['_items'][0]

        kiln = {
            'name': 'Test kiln',
            'user': user['_id'],
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
        r = self.post('api/kilns', data=kiln)
        kiln = r[0]

        # Create an image.
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        file_ = open(os.path.join(__location__, 'img.jpg'));
        file_content = file_.read()
        image = BytesIO(file_content)
        data = {
            'kiln': kiln['_id'],
            'file': (image, 'img.jpg'),
        }
        r = self.test_client.post('api/images', data=data)
        self.assertEqual(r.status_code, 201)

        # Check we have an image.
        r = self.get('api/images')
        total = r[0]['_meta']['total']
        self.assertEqual(total, 1)

    def test_conversations(self):
        user = {
            'auth0_id': 'bar'
        }
        r = self.post('api/users', data=user)
        r = self.get('api/users')
        user_one = r[0]['_items'][0]
        user_two = r[0]['_items'][1]
        conversation = {
            'participants': [
                user_one['_id'],
                user_two['_id']
            ]
        }
        r = self.post('api/conversations', data=conversation)
        self.assertEqual(r[1], 201)

        url = 'api/conversations?where={"participants":"%s"}' % (user_one['_id'])
        r = self.get(url)
        self.assertEqual(len(r[0]['_items'][0]['participants']), 2)
