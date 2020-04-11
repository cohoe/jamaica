import json
from flask import request
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.cocktails.serializers import cocktail_list_result, cocktail_search_index
from jamaica.v1.cocktails.parsers import cocktail_list_parser


from barbados.search.cocktail import CocktailSearch
from barbados.caches import CocktailNameCache
from barbados.models import CocktailModel
from barbados.factories import CocktailFactory
from barbados.serializers import ObjectSerializer

ns = api.namespace('v1/cocktails', description='Cocktail recipes.')


@ns.route('/')
class CocktailsCollection(Resource):

    @api.expect(cocktail_list_parser, validate=True) # @TODO validate doesnt work.
    @api.marshal_list_with(cocktail_list_result)
    def get(self):
        return CocktailSearch(**request.args).execute()


@ns.route('/<string:slug>')
@api.response(404, 'Cocktail slug not in database.')
class CocktailCollection(Resource):

    def get(self, slug):
        try:
            result = CocktailModel.get_by_slug(slug)
            c = CocktailFactory.model_to_obj(result)
            return ObjectSerializer.serialize(c, 'dict')
        except KeyError:
            ns.abort(404, 'Cocktail not found.', slug=slug)


@ns.route('/index')
class CocktailIndex(Resource):

    @api.marshal_with(cocktail_search_index)
    def get(self):
        return json.loads(CocktailNameCache.retrieve())
