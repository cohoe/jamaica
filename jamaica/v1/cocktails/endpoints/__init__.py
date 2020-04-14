import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.cocktails.serializers import CocktailIndex, CocktailSearchItem
from jamaica.v1.cocktails.parsers import cocktail_list_parser


from barbados.search.cocktail import CocktailSearch
from barbados.caches import CocktailNameCache
from barbados.models import CocktailModel
from barbados.factories import CocktailFactory
from barbados.serializers import ObjectSerializer

ns = api.namespace('v1/cocktails', description='Cocktail recipes.')


@ns.route('/')
class CocktailsEndpoint(Resource):

    # Amazingly it took finding this post to figure out how
    # this is supposed to work.
    # https://stackoverflow.com/questions/41227736/flask-something-more-strict-than-api-expect-for-input-data
    @api.expect(cocktail_list_parser, validate=True)
    @api.marshal_list_with(CocktailSearchItem)
    def get(self):
        """
        Get a simplified view of cocktails from search.
        :return: List of SearchResult Dicts
        """
        args = cocktail_list_parser.parse_args(strict=True)
        return CocktailSearch(**args).execute()


@ns.route('/<string:slug>')
@api.response(404, 'Cocktail slug not in database.')
class CocktailEndpoint(Resource):

    def get(self, slug):
        """
        Get a single cocktail from the database.
        :param slug:
        :return: Serialized Cocktail
        """
        try:
            result = CocktailModel.get_by_slug(slug)
            c = CocktailFactory.model_to_obj(result)
            return ObjectSerializer.serialize(c, 'dict')
        except KeyError:
            ns.abort(404, 'Cocktail not found.', slug=slug)


@ns.route('/index')
class CocktailIndexEndpoint(Resource):

    @api.marshal_with(CocktailIndex)
    def get(self):
        """
        Get a simplified list of all cocktails from cache.
        :return: List
        """
        return json.loads(CocktailNameCache.retrieve())
