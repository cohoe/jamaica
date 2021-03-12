from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.auth.serializers import UserItem

ns = api.namespace('v1/auth', description='Authentication.')

# from flask_security import auth_required, current_user, auth_token_required
from flask import request
# import flask_security.views
# from barbados.factories.user import UserFactory
# from barbados.serializers import ObjectSerializer
from flask_security.utils import get_post_logout_redirect

# https://github.com/capless/warrant

# from warrant import Cognito

from jamaica.settings import cognito_settings
from flask import session, redirect

from functools import wraps
from werkzeug.exceptions import Unauthorized
import urllib.parse
from jamaica.v1.auth.parsers import cognito_parser


from jamaica.app import aws_auth
from flask import jsonify


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'authentication' not in session:
            raise Unauthorized()
        return f(*args, **kwargs)

    return decorated


# u = Cognito(**cognito_settings)
# print(u)


@ns.route('/info')
class AuthInfoEndpoint(Resource):

    # @api.response(200, 'success')
    # @auth_required
    # @TODO this is still all kinds of busted
    @aws_auth.authentication_required
    def get(self):
        """
        Get information about the currently logged in session.
        :return:
        """
        # import json
        # return json.loads(current_user)
        # print(current_user.get_auth_token())
        # u = UserFactory.model_to_obj(current_user)
        # return ObjectSerializer.serialize(u, 'dict')
        print(session)

        from flask_awscognito.utils import get_state
        expected_state = get_state(aws_auth.user_pool_id, aws_auth.user_pool_client_id)
        print(expected_state)
        token = aws_auth.get_access_token(request.args)

        # print()
        # print(aws_auth.get_access_token())
        return {
            'access_token': token,
            'state': expected_state
        }


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
        # redirect_url = "%s?" % ()
        # https://www.urlencoder.io/python/
        # base_url = 'https://grantcohoe-amari-test.auth.us-east-1.amazoncognito.com/login'
        # redirect_url = "%s?client_id=%s&redirect_uri=%s&response_type=token" % (base_url, cognito_settings.get('client_id'), urllib.parse.quote('http://localhost:8080/api/v1/auth/login/redirect'))
        # return redirect(redirect_url)
        return redirect(aws_auth.get_sign_in_url())


    # @api.response(200, 'success')
    # @api.expect(UserItem, validate=True)
    # # @TODO marshal_with
    # def post(self):
    #     """
    #     Log in and add_base_attributescreate a new authentication session.
    #     Because I set SECURITY_BACKWARDS_COMPAT_AUTH_TOKEN in the settings we don't require the user
    #     to add a query param here to get the auth token. Since I don't support GET there isn't much
    #     risk of leaking the token on a GET request.
    #     https://stackoverflow.com/questions/27356877/token-based-authentication-with-flask-security-extension
    #     https://flask-security-too.readthedocs.io/en/stable/features.html?highlight=include_auth_token
    #     https://github.com/Flask-Middleware/flask-security/blob/master/flask_security/views.py
    #     :return:
    #     """
    #     # return flask_security.views.login()
    #     print(api.payload)
    #     usr = Cognito(**cognito_settings, username=api.payload.get('username'))
    #     usr.authenticate(api.payload.get('password'))
    #     authentication_data = {
    #         'refresh_token': usr.refresh_token,
    #         'id_token': usr.id_token,
    #         'access_token': usr.access_token,
    #         'foo': 'lolzwat',
    #     }
    #     session.update({'authentication': authentication_data})
    #     return authentication_data


@ns.route('/logout')
class AuthLogoutEndpoint(Resource):

    @api.response(200, 'success')
    # @TODO marshal_with
    def post(self):
        """
        Log out a session.
        :return:
        """
        # return flask_security.views.logout()
        pass


@ns.route('/login/redirect')
class AuthLoginRedirectEndpoint(Resource):

    @api.response(200, 'success')
    # @api.expect(cognito_parser, validate=True)
    def get(self):
        """
        Authentication login redirect callback handler.
        Reserved for any future usage.
        :return:
        """
        # args = cognito_parser.parse_args(strict=True)
        # https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-app-integration.html
        # https://github.com/awslabs/aws-support-tools/blob/master/Cognito/decode-verify-jwt/decode-verify-jwt.py
        # print(args)
        # Well shit.
        # https://stackoverflow.com/questions/53566536/python-get-url-fragment-identifier-with-flask
        # foo = request
        # print(foo)

        access_token = aws_auth.get_access_token(request.args)
        # session.update({'access_token': access_token})
        return {
            'access_token': access_token,
            'state': request.args.get('state')
        }


# @ns.route('/logout/redirect')
# class AuthLogoutRedirectEndpoint(Resource):
#
#     @api.response(200, 'success')
#     def get(self):
#         """
#         Authentication logout redirect callback handler.
#         Reserved for any future usage.
#         :return:
#         """
#         pass
