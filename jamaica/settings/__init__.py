from barbados.settings import Setting


def settings_to_dict(settings):
    """
    Convenience function to turn a dict of Setting objects into a dict
    of key: value pairs by actually doing the value lookup.
    :param settings: Dict of key: Setting.
    :return: Dict of key: value
    """
    resolved_settings = {}
    for key, setting in settings.items():
        if isinstance(setting, Setting):
            resolved_settings[key] = setting.get_value()
        else:
            resolved_settings[key] = setting
    return resolved_settings


# https://github.com/postrational/rest_api_demo/blob/master/rest_api_demo/settings.py
app_settings = {
    # Flask-Restplus settings
    # 'SWAGGER_UI_DOC_EXPANSION': Setting(path='/api/flask/swagger_ui_doc_expansion', default='list', type_=str),
    'RESTPLUS_VALIDATE': Setting(path='/api/flask/restplus_validate', default=True, type_=bool),
    'RESTPLUS_MASK_SWAGGER': Setting(path='/api/flask/restplus_mask_swagger', default=False, type_=bool),
    'ERROR_404_HELP': Setting(path='/api/flask/restplus_error_404_help', default=False, type_=bool),
    # https://flask-restplus.readthedocs.io/en/stable/mask.html
    'RESTPLUS_MASK_HEADER': Setting(path='/api/flask/restplus_mask_header', default=False, type_=bool),
    # # https://github.com/python-restx/flask-restx/issues/27
    'PROPAGATE_EXCEPTIONS': Setting(path='/api/flask/propagate_exceptions', default=False, type_=bool),
}

app_runtime = {
    'debug': Setting(path='/api/flask/debug', env='AMARI_FLASK_DEBUG', default=True, type_=bool),
    'host': Setting(path='/api/flask/host', env='AMARI_FLASK_HOST', default='0.0.0.0', type_=str),
    'port': Setting(path='/api/flask/port', env='AMARI_FLASK_PORT', default=8080, type_=int),
}

cors_settings = {
    'origins': Setting(path='/api/flask/cors_origins', default=['0.0.0.0:8080', '0.0.0.0:3000'], type_=list)
}

auth0_settings = {
    'name': 'auth0',
    'client_id': Setting(path='/auth/auth0/client_id', type_=str),
    'client_secret': Setting(path='/auth/auth0/client_secret', type_=str),
    'api_base_url': Setting(path='/auth/auth0/api_base_url', type_=str),
    'access_token_url': Setting(path='/auth/auth0/access_token_url', type_=str),
    'authorize_url': Setting(path='/auth/auth0/authorize_url', type_=str),
    'client_kwargs': {
        'scope': 'openid profile email',
    },
}
