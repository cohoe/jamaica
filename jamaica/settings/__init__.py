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
    # SECRET_KEY=Setting(path='/api/flask/secret_key', default='Testing!', type_=str),
)

runtime_settings = Settings(
    debug=Setting(path='/api/flask/debug', env='AMARI_FLASK_DEBUG', default=True, type_=bool),
    host=Setting(path='/api/flask/host', env='AMARI_FLASK_HOST', default='0.0.0.0', type_=str),
    port=Setting(path='/api/flask/port', env='AMARI_FLASK_PORT', default=8080, type_=int),
)

cors_settings = Settings(
    origins=Setting(path='/api/flask/cors_origins', default=['0.0.0.0:8080', '0.0.0.0:3000', 'http://localhost:3000'], type_=list)
)

cognito_settings = Settings(
    COGNITO_REGION=Setting(path='/auth/cognito/region', default='us-east-1', type_=str),
    COGNITO_USERPOOL_ID=Setting(path='/auth/cognito/user_pool_id', type_=str),
    COGNITO_APP_CLIENT_ID=Setting(path='/auth/cognito/client_id', type_=str),
    COGNITO_CHECK_TOKEN_EXPIRATION=Setting(path='/auth/cognito/check_token_expiration', default=False, type_=bool),
    COGNITO_JWT_HEADER_NAME=Setting(path='/auth/cognito/token_header_name', default='X-Jamaica-Authorization', type_=str),
    COGNITO_JWT_HEADER_PREFIX='Bearer',
    COGNITO_DOMAIN=Setting(path='/auth/cognito/domain', type_=str),
    COGNITO_LOGIN_REDIRECT_URL='http://localhost:8080/api/v1/auth/login/redirect',
    COGNITO_LOGOUT_REDIRECT_URL='http://localhost:8080/api/v1/auth/logout/redirect',
)
