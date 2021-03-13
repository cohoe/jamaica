from flask_cognito import cognito_auth_required, cognito_check_groups
from jamaica.settings import cognito_settings
from jamaica.v1.restx import api, ErrorModel
from urllib.parse import quote


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


def jamaica_authn_required():
    """
    Common decorator for a normal authenticated HTTP request.
    https://adamj.eu/tech/2020/04/01/how-to-combine-two-python-decorators/
    NOTE - this does NOT imply an HTTP 200 success. You are responsible for doing that
    on your own.
    :param function: Function to decorate.
    # @TODO This does not play nice with the cognito_check_groups decorator.
    :return: Decorated function.
    """

    def decorator(func):
        func = api.response(401, 'Unauthorized. You are not authenticated.', ErrorModel)(func)
        func = api.response(403, 'Forbidden. You were authenticated, but not allowed.', ErrorModel)(func)
        func = cognito_auth_required(func)
        return func

    return decorator


def jamaica_authz_required(groups=None):
    """
    Common decorator for authorization of an HTTP endpoint. Requires jamaica_authn_required
    to be first decorated on the endpoint.
    :param groups: List of group IDs. No value implies no groups.
    :return: Function
    """
    if groups is None:
        groups = []

    def decorator(function):
        return cognito_check_groups(groups=groups)(function)

    return decorator
