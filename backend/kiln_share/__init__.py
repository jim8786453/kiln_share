# -*- coding: utf-8 -*-

import os

from eve import Eve
from eve_swagger import swagger, add_documentation
from flask import current_app as app, abort

from kiln_share import settings
from kiln_share.storage import GridFSImageStorage


_MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
_SETTINGS_PATH = os.path.join(_MODULE_PATH, 'settings.py')


def create_app():
    # Create the Eve app.
    app = Eve(settings=_SETTINGS_PATH, media=GridFSImageStorage)

    # Register Swagger extension.
    app.register_blueprint(swagger)
    app.config['SWAGGER_INFO'] = {
        'title': 'Kiln Share',
        'version': '0.0.1',
        'description': 'Backend Api for kilnshare.co.uk',
        'contact': {
            'name': 'jim8786453@gmail.com',
        },
    }

    return app


app = create_app()
