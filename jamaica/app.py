#!/usr/bin/env python3

from flask import Flask, Blueprint
from jamaica.cache import flask_cache
from flask_cors import CORS
from flask_sqlalchemy_session import flask_scoped_session
from flask_uuid import FlaskUUID
from jamaica.settings import app_settings, runtime_settings, cors_settings
from jamaica.v1.restx import api
from barbados.services.database import DatabaseService

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

### Auth Stuff

# https://flask-security-too.readthedocs.io/en/stable/quickstart.html#basic-sqlalchemy-application-with-session
# from flask_security import SQLAlchemySessionUserDatastore, Security, hash_password
# from barbados.models.user import UserModel
# from barbados.models.role import RoleModel
# from barbados.models.userrolebinding import UserRoleBindingModel
# user_datastore = SQLAlchemySessionUserDatastore(session, UserModel, RoleModel)
# security = Security(app, user_datastore, register_blueprint=False)
#
# UserModel.query = session.query_property()
#
#
# from flask_awscognito import AWSCognitoAuthentication
# from functools import wraps
# from flask_awscognito.utils import extract_access_token
# from flask_awscognito.exceptions import TokenVerifyError
# from flask import request, abort, g
#
#
# class JamaicaCognito(AWSCognitoAuthentication):
#
#     def authentication_required(self, view):
#         @wraps(view)
#         def decorated(*args, **kwargs):
#             if not self.app.config.get("TESTING"):
#                 access_token = extract_access_token(request.headers)
#                 try:
#                     self.token_service.verify(access_token)
#                     self.claims = self.token_service.claims
#                     g.cognito_claims = self.claims
#                 except TokenVerifyError as e:
#                     _ = request.data
#                     # abort(401, response=make_response(jsonify(message=str(e)), 401))
#                     # The way this is exists in the normal thing doesn't work
#                     # Had to go my own way. RIP.
#                     abort(status=401, description=str(e))
#                     # abort(make_response(jsonify(message=str(e)), 401))
#
#             return view(*args, **kwargs)
#         return decorated
#
#
# aws_auth = JamaicaCognito(app)
#
#
#
# @app.before_first_request
# def create_user():
#     DatabaseService.connector.create_all()
#     if not user_datastore.find_user(email="test@me.com"):
#         user_datastore.create_user(email="test@me.com", password=hash_password("password"))
#     session.commit()


from flask_cognito import CognitoAuth
cogauth = CognitoAuth(app)



### End Auth Stuff


def main():
    initialize_endpoints(app)
    setup_cors(app)
    setup_cache(app)
    app.run(**runtime_settings)


if __name__ == "__main__":
    main()
