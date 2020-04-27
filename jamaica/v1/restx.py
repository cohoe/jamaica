from flask_restx import Api, fields
from jamaica import settings
# from jamaica import serializers
from sqlalchemy.exc import IntegrityError

api = Api(version='0.0.1', title='Jamaica API')

ErrorModel = api.model('ErrorModel', {
    'message': fields.String(example="It's the wrong trousers! They've gone wrong!"),
})


# https://github.com/postrational/rest_api_demo/blob/master/rest_api_demo/api/restplus.py
# https://flask-restx.readthedocs.io/en/latest/errors.html
@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


@api.marshal_with(ErrorModel, code=404)
@api.errorhandler(KeyError)
def key_error_handler(error):
    """
    KeyError generally means the object was not found.
    :param error:
    :return:
    """
    return {'message': str(error)}, 404


@api.marshal_with(ErrorModel, code=400)
@api.errorhandler(IntegrityError)
def integrity_error_handler(error):
    """
    Database integrity problem (duplicate, invalid key, etc).
    :param error:
    :return:
    """
    message = error.orig.diag.message_detail
    return {'message': message}, 400
