from flask_restx import Resource
from jamaica.v1.restx import api

ns = api.namespace('v1/auth', description='Authentication.')

from flask_security import auth_required, current_user, auth_token_required
from flask import request
import flask_security.views


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
        print(current_user.id, current_user.email, current_user.username)


@ns.route('/login')
class AuthLoginEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Log in and create a new authentication setting.
        :return:
        """
        pass

    @api.response(200, 'success')
    def post(self):
        """
        Log in and create a new authentication setting.
        :return:
        """
        print(request.is_json)
        print(request.args)
        return flask_security.views.login()



@ns.route('/logout')
class AuthLogoutEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Log out a session.
        :return:
        """
        pass


@ns.route('/redirect')
class AuthRedirectEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Authentication redirect callback handler.
        :return:
        """
        pass
