import os
from flask import url_for
from flask_restx import Api, fields
from jamaica import settings
# from jamaica import serializers
from sqlalchemy.exc import IntegrityError
from barbados.exceptions import ValidationException, ServiceUnavailableException, FactoryUpdateException


class CustomApi(Api):
    @property
    def specs_url(self):
        """
        Monkey patch for HTTPS.
        https://github.com/noirbizarre/flask-restplus/issues/223
        https://stackoverflow.com/questions/47508257/serving-flask-restplus-on-https-server
        """
        scheme = 'https' if os.environ.get('KUBERNETES_PORT') else 'http'
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)


api = CustomApi(version='0.0.1', title='Jamaica API')

ErrorModel = api.model('ErrorModel', {
    'message': fields.String(example="It's the wrong trousers! They've gone wrong!"),
    'details': fields.String(example="The evil chicken stole the trousers.")
})


# https://github.com/postrational/rest_api_demo/blob/master/rest_api_demo/api/restplus.py
# https://flask-restx.readthedocs.io/en/latest/errors.html
@api.marshal_with(ErrorModel, code=500)
@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    details = str(e)

    # if settings.FLASK_DEBUG:
    # @TODO this probably isn't cool in production.
    return {'message': message, 'details': details}, 500


@api.marshal_with(ErrorModel, code=404)
@api.errorhandler(KeyError)
def key_error_handler(error):
    """
    KeyError generally means the object was not found.
    :param error:
    :return:
    """
    # For some reason something is adding quotes to the error
    # message, thus doubling up on the output quotes.
    # https://stackoverflow.com/questions/40950791/remove-quotes-from-string-in-python
    #
    # Apparently its expected?
    # https://stackoverflow.com/questions/24998968/why-does-strkeyerror-add-extra-quotes
    # @TODO get this to the rest of the handlers. Though not sure it's needed?
    message = str(error).strip('"').strip("'")
    return {'message': message, 'details': str(error)}, 404


@api.marshal_with(ErrorModel, code=404)
@api.errorhandler(ValueError)
def key_error_handler(error):
    """
    ValueError generally means the object was not found.
    :param error:
    :return:
    """
    # For some reason something is adding quotes to the error
    # message, thus doubling up on the output quotes.
    # https://stackoverflow.com/questions/40950791/remove-quotes-from-string-in-python
    # @TODO get this to the rest of the handlers.
    message = str(error).strip('"')
    return {'message': message}, 404


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


@api.marshal_with(ErrorModel, code=400)
@api.errorhandler(ValidationException)
@api.errorhandler(FactoryUpdateException)
def validation_error_handler(error):
    """
    ObjectValidator failed.
    :param error: 
    :return:
    """
    return {'message': str(error)}, 400


@api.marshal_with(ErrorModel, code=500)
@api.errorhandler(ServiceUnavailableException)
def service_error_handler(error):
    """
    Some internal service is not available
    :param error:
    :return:
    """
    return {'message': 'A necessary internal service is unavailable. ' + str(error)}, 500
