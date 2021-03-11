from flask_restx import reqparse, inputs

cognito_parser = reqparse.RequestParser()
cognito_parser.add_argument('id_token', type=str, required=True)
cognito_parser.add_argument('access_token', type=str, required=True)
cognito_parser.add_argument('expires_in', type=int, required=True)
cognito_parser.add_argument('token_type', type=str, required=True)
