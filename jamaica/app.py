#!/usr/bin/env python3

from flask import Flask, Blueprint
from jamaica.cache import flask_cache
from flask_cors import CORS
from flask_sqlalchemy_session import flask_scoped_session
from flask_uuid import FlaskUUID
from jamaica.settings import app_settings, runtime_settings, cors_settings, cognito_settings
from jamaica.v1.restx import api
from barbados.services.database import DatabaseService
from flask_cognito import CognitoAuth

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
    flask_app.config.update(app_settings)


def initialize_endpoints(flask_app):
    """
    Setup the various API endpoints.
    :param flask_app: flask.Flask instance.
    :return: None
    """
    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)

    namespaces = [
        jamaica.v1.cocktails.endpoints.ns,
        jamaica.v1.ingredients.endpoints.ns,
        jamaica.v1.lists.endpoints.ns,
        jamaica.v1.caches.endpoints.ns,
        jamaica.v1.inventories.endpoints.ns,
        jamaica.v1.indexes.endpoints.ns,
        jamaica.v1.setup.endpoints.ns,
        jamaica.v1.constructions.endpoints.ns,
        jamaica.v1.glassware.endpoints.ns,
        jamaica.v1.auth.endpoints.ns,
    ]
    for ns in namespaces:
        api.add_namespace(ns)

    flask_app.register_blueprint(blueprint)


def setup_cors(flask_app):
    CORS(flask_app, **cors_settings)


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

# Authentication
app.config.update(cognito_settings)
cogauth = CognitoAuth(app)


def main():
    initialize_endpoints(app)
    setup_cors(app)
    setup_cache(app)
    app.run(**runtime_settings)


if __name__ == "__main__":
    main()
