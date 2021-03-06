from flask_restx import Resource
from jamaica.v1.restx import api

from jamaica.app import auth0#, requires_auth
from flask import session, redirect
from six.moves.urllib.parse import urlencode
from jamaica.settings import auth0_settings

ns = api.namespace('v1/auth', description='Authentication.')


from functools import wraps
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            # Redirect to Login page here
            # return redirect('/api/v1/auth/login')
            return redirect('/api/v1/auth/login')
        return f(*args, **kwargs)

    return decorated


# https://auth0.com/docs/quickstart/webapp/python/01-login
@ns.route('/info')
class AuthInfoEndpoint(Resource):

    @requires_auth
    @api.response(200, 'success')
    def get(self):
        """
        Get information about the currently logged in session.
        :return:
        """
        return session.get('jwt_payload')


@ns.route('/login')
class AuthLoginEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Log in and create a new authentication setting.
        :return:
        """
        return auth0.authorize_redirect(redirect_uri='http://localhost:8080/api/v1/auth/redirect')

    @api.response(200, 'success')
    def post(self):
        """
        Log in and create a new authentication setting.
        :return:
        """
        pass


@ns.route('/logout')
class AuthLogoutEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Log out a session.
        :return:
        """
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {'returnTo': 'http://localhost:8080/api/', 'client_id': auth0_settings.get('client_id').get_value()}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@ns.route('/redirect')
class AuthRedirectEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Authentication redirect callback handler.
        :return:
        """
        # Handles response from token endpoint
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        # Store the user information in flask session.
        session['jwt_payload'] = userinfo
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
        return redirect('/api/v1/auth/info')
