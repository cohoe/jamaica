from barbados.settings import Setting, Settings

# https://github.com/postrational/rest_api_demo/blob/master/rest_api_demo/settings.py
app_settings = Settings(
    # Flask-Restplus settings
    SWAGGER_UI_DOC_EXPANSION=Setting(path='/api/flask/swagger_ui_doc_expansion', default='list', type_=str),
    RESTPLUS_VALIDATE=Setting(path='/api/flask/restplus_validate', default=True, type_=bool),
    RESTPLUS_MASK_SWAGGER=Setting(path='/api/flask/restplus_mask_swagger', default=False, type_=bool),
    ERROR_404_HELP=Setting(path='/api/flask/restplus_error_404_help', default=False, type_=bool),
    # https://flask-restplus.readthedocs.io/en/stable/mask.html
    RESTPLUS_MASK_HEADER=Setting(path='/api/flask/restplus_mask_header', default=False, type_=bool),
    # # https://github.com/python-restx/flask-restx/issues/27
    PROPAGATE_EXCEPTIONS=Setting(path='/api/flask/propagate_exceptions', default=False, type_=bool),
    # https://stackoverflow.com/questions/26080872/secret-key-not-set-in-flask-session-using-the-flask-session-extension
    SECRET_KEY=Setting(path='/api/flask/secret_key', default='Testing!', type_=str),
    SECURITY_PASSWORD_SALT=Setting('/api/flask/security_password_salt', default='123123123', type_=str)
)

runtime_settings = Settings(
    debug=Setting(path='/api/flask/debug', env='AMARI_FLASK_DEBUG', default=True, type_=bool),
    host=Setting(path='/api/flask/host', env='AMARI_FLASK_HOST', default='0.0.0.0', type_=str),
    port=Setting(path='/api/flask/port', env='AMARI_FLASK_PORT', default=8080, type_=int),
)

cors_settings = Settings(
    origins=Setting(path='/api/flask/cors_origins', default=['0.0.0.0:8080', '0.0.0.0:3000'], type_=list)
)
