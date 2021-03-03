from flask_restx import Resource
from jamaica.v1.restx import api

ns = api.namespace('v1/auth', description='Authentication.')


@ns.route('')
class AuthEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Get information about the currently logged in session.
        :return:
        """
        pass


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
        pass


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
        Authentication redirect handler.
        :return:
        """
        pass
