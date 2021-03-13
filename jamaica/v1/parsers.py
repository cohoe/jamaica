from flask_restx import reqparse, inputs
from jamaica.settings import cognito_settings

auth_parser = reqparse.RequestParser()
auth_parser.add_argument(cognito_settings.get('COGNITO_JWT_HEADER_NAME'), type=str, location='headers',
                         help="API token with usage prefix. Example: \"Bearer abc123l0l\"")
