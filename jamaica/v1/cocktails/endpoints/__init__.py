import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.serializers import CocktailSearchItem
from jamaica.v1.cocktails.serializers import CocktailItem, CitationItem
from jamaica.v1.cocktails.parsers import cocktail_list_parser
from flask_sqlalchemy_session import current_session

from barbados.search.cocktail import CocktailSearch
from barbados.caches.tablescan import CocktailScanCache
from barbados.caches.recipebibliography import RecipeBibliographyCache
from barbados.factories import CocktailFactory
from barbados.serializers import ObjectSerializer
from barbados.indexers.recipe import RecipeIndexer

ns = api.namespace('v1/cocktails', description='Cocktail recipes.')


@ns.route('/')
class CocktailsEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(CocktailItem)
    def get(self):
        """
        Return a list of all fully-detailed cocktail objects
        :return: List[Dict]
        """
        serialized_cocktails = json.loads(CocktailScanCache.retrieve())
        return serialized_cocktails

    @api.response(200, 'success')
    @api.expect(CocktailItem, validate=True)
    @api.marshal_list_with(CocktailItem)
    def post(self):
        """
        Create a new cocktail.
        :return: Serialized Cocktail object.
        """
        c = CocktailFactory.raw_to_obj(api.payload, api.payload.get('slug'))
        CocktailFactory.store_obj(session=current_session, obj=c)
        RecipeIndexer.index(c)

        # Invalidate Cache
        CocktailScanCache.invalidate()

        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self):
        """
        Delete all cocktails from the database. There be dragons here.
        :return: Number of items deleted.
        """
        objects = CocktailFactory.produce_all_objs(session=current_session)
        for c in objects:
            CocktailFactory.delete_obj(session=current_session, obj=c, commit=False)

        RecipeIndexer.empty()
        current_session.commit()
        CocktailScanCache.invalidate()

        return len(objects)


@ns.route('/search')
class CocktailSearchEndpoint(Resource):
    # Amazingly it took finding this post to figure out how
    # this is supposed to work.
    # https://stackoverflow.com/questions/41227736/flask-something-more-strict-than-api-expect-for-input-data
    @api.response(200, 'success')
    @api.expect(cocktail_list_parser, validate=True)
    @api.marshal_list_with(CocktailSearchItem)
    def get(self):
        """
        Get a simplified view of cocktails from search. No search parameters means
        empty list for you.
        :return: List of SearchResult Dicts
        """
        args = cocktail_list_parser.parse_args(strict=True)

        # Don't return any results if all parameters are empty.
        # https://stackoverflow.com/questions/35253971/how-to-check-if-all-values-of-a-dictionary-are-0
        if all(value is None for value in args.values()):
            return []

        return CocktailSearch(**args).execute()


@ns.route('/<string:slug>')
class CocktailEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(CocktailItem)
    def get(self, slug):
        """
        Get a single cocktail from the database.
        :param slug:
        :return: Serialized Cocktail
        :raises IntegrityError: Duplicate
        """
        c = CocktailFactory.produce_obj(session=current_session, id=slug)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, slug):
        """
        Delete a single cocktail from the database.
        :param slug:
        :return:
        """
        c = CocktailFactory.produce_obj(session=current_session, id=slug)
        CocktailFactory.delete_obj(session=current_session, obj=c)

        CocktailScanCache.invalidate()
        RecipeIndexer.delete(c)


@ns.route('/bibliography')
class CocktailBibliographyEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(CitationItem)
    def get(self):
        """
        Return a list of all Citation objects associated with every
        cocktail in the database. Citation needed? I think not!
        :return: List[Citation]
        """
        serialized_citations = json.loads(RecipeBibliographyCache.retrieve())
        return serialized_citations
