from flask_restx import Resource
from jamaica.v1.restx import api

from jamaica.settings import cognito_settings
from flask import session, redirect, jsonify
from urllib.parse import quote
from flask_cognito import cognito_auth_required, current_cognito_jwt, cognito_check_groups
from jamaica.v1.parsers import auth_parser
from jamaica.v1.restx import ErrorModel

ns = api.namespace('v1/auth', description='Authentication.')


def get_sign_in_url():
    """
    Get the Cognito Sign-in URL.
    This was lifted from the Flask-AWSCognito module (not to be confused with Flask-Cognito).
    :return: String
    """
    return (
        f"{cognito_settings.get('COGNITO_DOMAIN')}/login"
        f"?response_type=token"
        f"&client_id={cognito_settings.get('COGNITO_APP_CLIENT_ID')}"
        f"&redirect_uri={quote(cognito_settings.get('COGNITO_LOGIN_REDIRECT_URL'))}"
    )


def get_sign_out_url():
    """
    Get the Cognito Sign-out URL.
    :return: String
    """
    return (
        f"{cognito_settings.get('COGNITO_DOMAIN')}/logout"
        f"?client_id={cognito_settings.get('COGNITO_APP_CLIENT_ID')}"
        f"&logout_uri={quote(cognito_settings.get('COGNITO_LOGOUT_REDIRECT_URL'))}"
    )


def jamaica_auth_required(groups=[]):
    """
    Common decorator for a normal authenticated HTTP request.
    https://adamj.eu/tech/2020/04/01/how-to-combine-two-python-decorators/
    NOTE - this does NOT imply an HTTP 200 success. You are responsible for doing that
    on your own.
    :return: Decorated function.
    """

    def decorator(func):
        # func = api.response(401, 'Unauthorized. You are not authenticated.', ErrorModel)(func)
        # func = api.response(403, 'Forbidden. You were authenticated, but not allowed.', ErrorModel)(func)
        func = cognito_auth_required(func)
        # print(groups)
        # if groups:
        #     func = cognito_group_permissions(groups)(func)
        func = cognito_check_groups(groups)(func)
        return func

    return decorator


@ns.route('/info')
class AuthInfoEndpoint(Resource):

    @api.response(200, 'success')
    @jamaica_auth_required(groups=['admins'])
    # @cognito_check_groups(['admins'])
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
