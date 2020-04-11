# https://github.com/postrational/rest_api_demo/blob/master/rest_api_demo/settings.py

# Flask settings
FLASK_DEBUG = True

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False
# https://flask-restplus.readthedocs.io/en/stable/mask.html
RESTPLUS_MASK_HEADER = False