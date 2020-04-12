from flask_restx import Api
from jamaica import settings

api = Api(version='0.0.1', title='Jamaica API')


# https://github.com/postrational/rest_api_demo/blob/master/rest_api_demo/api/restplus.py
@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500
