from flask_restx import reqparse

ingredient_list_parser = reqparse.RequestParser()
ingredient_list_parser.add_argument('name', type=str, help='Partial ingredient name.')
ingredient_list_parser.add_argument('kind', type=str, help='Ingredient kind.')
