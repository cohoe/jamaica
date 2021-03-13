from flask_restx import Resource
from jamaica.v1.restx import api

from flask import session, redirect, jsonify
from flask_cognito import current_cognito_jwt
from jamaica.auth import jamaica_authn_required, jamaica_authz_required, get_sign_in_url, get_sign_out_url

ns = api.namespace('v1/auth', description='Authentication.')


@ns.route('/info')
class AuthInfoEndpoint(Resource):

    @api.response(200, 'success')
    @jamaica_authn_required()
    # @jamaica_authz_required()
    def get(self):
        """
        Get information about the currently logged in session.
        :return:
        """
        return jsonify(dict(current_cognito_jwt))


@ns.route('/login')
class AuthLoginEndpoint(Resource):

    @api.response(302, 'redirect')
    def get(self):
        """
        Return a redirect to the Cognito sign-in URL.
        :return: HTTP 302
        """
        return redirect(get_sign_in_url())


@ns.route('/logout')
class AuthLogoutEndpoint(Resource):

    @api.response(302, 'success')
    def get(self):
        """
        Log out a session.
        :return:
        """
        session.clear()
        return redirect(get_sign_out_url())


@ns.route('/login/redirect')
class AuthLoginRedirectEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Authentication login redirect callback handler.
        Reserved for any future usage.
        :return:
        """
        return {'message': "Token is in the URL fragment above."}


@ns.route('/logout/redirect')
class AuthLogoutRedirectEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Authentication logout redirect callback handler.
        :return:
        """
        return {'message': "This does not expire your token. Can't do that."}
