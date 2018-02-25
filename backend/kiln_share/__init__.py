# -*- coding: utf-8 -*-

import os

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
        """ Validates the the current request is allowed to pass through.
        :param allowed_roles: allowed roles for the current request, can be a
                              string or a list of roles.
        :param resource: resource being requested.
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


def create_app():
    # Create the Eve app.
    app = Eve(auth=Auth, settings=_SETTINGS_PATH,
              media=GridFSImageStorage)

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
