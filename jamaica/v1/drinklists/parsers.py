from flask_restx import reqparse

drinklist_list_parser = reqparse.RequestParser()
drinklist_list_parser.add_argument('cocktail_slug', type=str, help='Partial cocktail slug.')
drinklist_list_parser.add_argument('name', type=str, help='Name of the drinklist.')
