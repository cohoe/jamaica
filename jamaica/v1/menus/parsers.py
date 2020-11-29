from flask_restx import reqparse

menu_list_parser = reqparse.RequestParser()
menu_list_parser.add_argument('cocktail_slug', type=str, help='Partial cocktail slug.')
menu_list_parser.add_argument('name', type=str, help='Name of the menu.')
