from flask_restx import reqparse

cocktail_list_parser = reqparse.RequestParser()
cocktail_list_parser.add_argument('name', type=str, help='Partial cocktail or spec name.')
cocktail_list_parser.add_argument('components', type=str, action='split', help='Comma-seperated list of components.')
cocktail_list_parser.add_argument('alpha', type=str, help='Single character to search by (or # aka %23 for numbers).')
cocktail_list_parser.add_argument('construction', type=str, help='Drink construction.')
cocktail_list_parser.add_argument('component_count', type=int, help='Count of components.')
