#!/usr/bin/env python3

from flask import Flask, Blueprint
from jamaica.cache import flask_cache
from flask_cors import CORS
from flask_sqlalchemy_session import flask_scoped_session
from flask_uuid import FlaskUUID
from jamaica.settings import settings_to_dict, app_settings, app_runtime, cors_settings, auth0_settings
from jamaica.v1.restx import api
from barbados.services.database import DatabaseService
from barbados.settings import Setting

# Endpoints
import jamaica.v1.cocktails.endpoints
import jamaica.v1.ingredients.endpoints
import jamaica.v1.lists.endpoints
import jamaica.v1.caches.endpoints
import jamaica.v1.inventories.endpoints
import jamaica.v1.indexes.endpoints
import jamaica.v1.setup.endpoints
import jamaica.v1.constructions.endpoints
import jamaica.v1.glassware.endpoints
import jamaica.v1.auth.endpoints


def configure_app(flask_app):
    """
    Configure the Flask instance with any special parameters.
    https://github.com/postrational/rest_api_demo/blob/master/rest_api_demo/app.py
    :param flask_app: flask.Flask instance.
    :return: None
    """
    for key, setting in app_settings.items():
        flask_app.config[key] = setting.get_value()


def initialize_endpoints(flask_app):
    """
    Setup the various API endpoints.
    :param flask_app: flask.Flask instance.
    :return: None
    """
    blueprint = Blueprint('api', __name__, url_prefix='/api')

    api.init_app(blueprint)
    api.add_namespace(jamaica.v1.cocktails.endpoints.ns)
    api.add_namespace(jamaica.v1.ingredients.endpoints.ns)
    api.add_namespace(jamaica.v1.lists.endpoints.ns)
    api.add_namespace(jamaica.v1.caches.endpoints.ns)
    api.add_namespace(jamaica.v1.inventories.endpoints.ns)
    api.add_namespace(jamaica.v1.indexes.endpoints.ns)
    api.add_namespace(jamaica.v1.setup.endpoints.ns)
    api.add_namespace(jamaica.v1.constructions.endpoints.ns)
    api.add_namespace(jamaica.v1.glassware.endpoints.ns)
    api.add_namespace(jamaica.v1.auth.endpoints.ns)

    flask_app.register_blueprint(blueprint)


def setup_cors(flask_app):
    CORS(flask_app, **settings_to_dict(cors_settings))


def setup_cache(flask_app):
    """
    Setup endpoint caching.
    :param flask_app:
    :return:
    """
    flask_cache.init_app(flask_app)

    # @TODO disable this when we get real
    with flask_app.app_context():
        flask_cache.clear()


app = Flask('jamaica')
configure_app(app)

# Dependent service setup
# This doesn't use get_session. https://flask-sqlalchemy-session.readthedocs.io/en/v1.1/
session = flask_scoped_session(DatabaseService.connector.Session, app)
# https://github.com/wbolster/flask-uuid
FlaskUUID(app)


from authlib.integrations.flask_client import OAuth
oauth = OAuth(app)

auth0 = oauth.register(**settings_to_dict(auth0_settings))

# https://stackoverflow.com/questions/26080872/secret-key-not-set-in-flask-session-using-the-flask-session-extension
app.secret_key = Setting(path='/api/flask/secret_key', type_=str).get_value()


def main():
    initialize_endpoints(app)
    setup_cors(app)
    setup_cache(app)
    app.run(**settings_to_dict(app_runtime))


if __name__ == "__main__":
    main()
