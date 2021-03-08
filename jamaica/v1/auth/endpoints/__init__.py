from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.auth.serializers import UserItem

ns = api.namespace('v1/auth', description='Authentication.')

from flask_security import auth_required, current_user, auth_token_required
from flask import request
import flask_security.views
from barbados.factories.user import UserFactory
from barbados.serializers import ObjectSerializer


@ns.route('/info')
class AuthInfoEndpoint(Resource):

    @api.response(200, 'success')
    # https://stackoverflow.com/questions/28727954/how-to-get-auth-token-required-in-flask-security-working
    @auth_token_required
    def get(self):
        """
        Get information about the currently logged in session.
        :return:
        """
        # import json
        # return json.loads(current_user)
        u = UserFactory.model_to_obj(current_user)
        return ObjectSerializer.serialize(u, 'dict')


@ns.route('/login')
class AuthLoginEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Log in and create a new authentication session.
        Reserved in case I ever use a service that needs a function
        to redirect to the service.
        :return:
        """
        pass

    @api.response(200, 'success')
    @api.expect(UserItem, validate=True)
    # @TODO marshall_with
    def post(self):
        """
        Log in and create a new authentication session.
        :return:
        """
        return flask_security.views.login()


@ns.route('/logout')
class AuthLogoutEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Log out a session.
        :return:
        """
        return flask_security.views.logout()


@ns.route('/redirect')
class AuthRedirectEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Authentication redirect callback handler.
        :return:
        """
        pass
