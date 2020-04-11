from flask_restx import reqparse

# @TODO even with validate=True, this doeesn't seem to actually do anything other than document.
cocktail_list_parser = reqparse.RequestParser()
cocktail_list_parser.add_argument('name', type=str, help='Partial cocktail or spec name.')
cocktail_list_parser.add_argument('components', type=str, help='Comma-seperated list of components.')
cocktail_list_parser.add_argument('alpha', type=str, help='Single character to search by (or #/%23 for numbers).')