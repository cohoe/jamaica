import copy
from flask_restx import reqparse
from jamaica.v1.cocktails.parsers import cocktail_list_parser

inventory_resolve_parser = reqparse.RequestParser()
inventory_resolve_parser.add_argument('cocktail', type=str, help='cocktail slug')
inventory_resolve_parser.add_argument('spec', type=str, help='spec slug from the cocktail')
# @TODO inventory resolution
# inventory_resolve_parser.add_argument('ingredient', type=str, help='cocktail slug')

# This matches everything that the cocktail_list_parser can do.
inventory_recipes_parser = copy.deepcopy(cocktail_list_parser)
inventory_recipes_parser.add_argument('missing', type=str, help='Count of missing')
