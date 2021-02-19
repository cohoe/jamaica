from flask_restx import reqparse

list_parser = reqparse.RequestParser()
list_parser.add_argument('cocktail_slug', type=str, help='Partial cocktail slug.')
list_parser.add_argument('name', type=str, help='Name of the list.')
