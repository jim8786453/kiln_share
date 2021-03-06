# -*- coding: utf-8 -*-

import json
import os

from copy import deepcopy

from eve import Eve
from eve.auth import TokenAuth
from eve_swagger import swagger, add_documentation
from flask import current_app as app, abort, request

from kiln_share import settings
from kiln_share.storage import GridFSImageStorage


_MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
_SETTINGS_PATH = os.path.join(_MODULE_PATH, 'settings.py')


class Auth(TokenAuth):
    """Checks the HTTP 'Authorization' header has been set with an Auth0
    identifier. This will have been added by an upstream proxy.

    """

    def authorized(self, allowed_roles, resource, method):
        """Validates the the current request is allowed to pass through.

        """
        auth = None
        if 'X-Kiln-Share-Id' in request.headers:
            auth = request.headers.get('X-Kiln-Share-Id')

        if auth:
            self.set_request_auth_value(auth)

        return auth and self.check_auth(auth, allowed_roles,
                                        resource, method)

    def check_auth(self, token, allowed_roles, resource, method):
        users = app.data.driver.db['users']
        user = users.find_one({'auth0_id': token})
        if user:
            return user

        settings.logger.info('Creating user %s' % token)
        user = users.insert({'auth0_id': token})
        return user


def on_insert_conversations(items):
    """Combine the posted contents of participants with the current
    authorised user so all users can see the conversation.

    """
    data = json.loads(request.data)
    if not isinstance(data, list):
        data = [data]

    for (d, i) in zip(data, items):
        p = deepcopy(i['participants'])
        d['participants'].append(p)
        i['participants'] = d['participants']


def on_pre_GET_conversations(request, lookup):
    """Ensure the current user is included in the lookup.

    """
    user = request.headers['X-Kiln-Share-Id']
    lookup['participants'] = user


def on_insert_messages(items):
    """Check the user is a participant in the conversation.

    """
    collection = app.data.driver.db['conversations']
    conversation_ids = [item['conversation'] for item in items]
    conversations = collection.find({'_id': item['conversation']})
    # From value will be the same in all items.
    from_ = items[0]['from']
    for conversation in conversations:
        if from_ not in conversation['participants']:
            abort(403)


def on_fetched_item_conversations(response):
    """Add the messages into the conversation response.

    """
    conversation_id = response['_id']
    collection = app.data.driver.db['messages']
    response['messages'] = [message for message in collection.find(
        {'conversation': conversation_id})]


def create_app():
    # Create the Eve app.
    app = Eve(auth=Auth, settings=_SETTINGS_PATH,
              media=GridFSImageStorage)

    # Events
    app.on_insert_conversations += on_insert_conversations
    app.on_pre_GET_conversations += on_pre_GET_conversations
    app.on_insert_messages += on_insert_messages
    app.on_fetched_item_conversations += on_fetched_item_conversations

    # Register Swagger extension.
    app.register_blueprint(swagger, url_prefix='/auth')
    app.config['SWAGGER_INFO'] = {
        'title': 'Kiln Share',
        'version': '0.0.1',
        'description': 'Backend Api for kilnshare.co.uk',
        'contact': {
            'name': 'jim@kohlstudios.co.uk',
        },
        'schemes': ['https'],
    }

    return app


app = create_app()
