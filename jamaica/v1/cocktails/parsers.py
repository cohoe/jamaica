from flask_restx import reqparse, inputs

cocktail_list_parser = reqparse.RequestParser()
cocktail_list_parser.add_argument('name', type=str, help='Partial cocktail or spec name.')
cocktail_list_parser.add_argument('components', type=str, action='split', help='Comma-seperated list of components.')
cocktail_list_parser.add_argument('no_components', type=str, action='split', help='Comma-seperated list of components to exclude.')
cocktail_list_parser.add_argument('alpha', type=str, help='Single character to search by (or # aka %23 for numbers).')
cocktail_list_parser.add_argument('construction', type=str, help='Drink construction.')
cocktail_list_parser.add_argument('component_count', type=int, help='Count of components.')
# https://github.com/noirbizarre/flask-restplus/issues/199
cocktail_list_parser.add_argument('garnish', type=inputs.boolean, help='Boolean of if results should have garnish.')
cocktail_list_parser.add_argument('citation_name', type=str, help='Citation name keyword')
cocktail_list_parser.add_argument('citation_author', type=str, help='Citation author keyword')
cocktail_list_parser.add_argument('instructions', type=str, help='String in instructions')
