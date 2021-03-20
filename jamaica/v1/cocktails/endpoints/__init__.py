import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.serializers import CocktailSearchItem, TextItem
from jamaica.v1.cocktails.serializers import CocktailItem, CitationItem
from jamaica.v1.cocktails.parsers import cocktail_list_parser
from flask_sqlalchemy_session import current_session

from barbados.search.cocktail import CocktailSearch
from barbados.caches.tablescan import CocktailScanCache
from barbados.caches.recipebibliography import RecipeBibliographyCache
from barbados.caches.notebook import NotebookCache
from barbados.factories.cocktail import CocktailFactory
from barbados.serializers import ObjectSerializer
from barbados.indexers.recipe import RecipeIndexer

ns = api.namespace('v1/cocktails', description='Cocktail recipes.')


@ns.route('')
class CocktailsEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(CocktailItem)
    def get(self):
        """
        Return a list of all fully-detailed cocktail objects
        :return: List[Dict]
        """
        serialized_cocktails = CocktailScanCache.retrieve()
        return serialized_cocktails

    @api.response(201, 'created')
    @api.expect(CocktailItem, validate=True)
    @api.marshal_list_with(CocktailItem)
    def post(self):
        """
        Create a new cocktail.
        :return: Serialized Cocktail object.
        """
        c = CocktailFactory.raw_to_obj(api.payload)
        CocktailFactory.insert_obj(obj=c)
        RecipeIndexer.index(c)

        # Invalidate Cache
        CocktailScanCache.invalidate()

        return ObjectSerializer.serialize(c, 'dict'), 201

    @api.response(204, 'successful delete')
    def delete(self):
        """
        Delete all cocktails from the database. There be dragons here.
        :return: Number of items deleted.
        """
        objects = CocktailFactory.produce_all_objs()
        for c in objects:
            CocktailFactory.delete_obj(obj=c, commit=False)

        RecipeIndexer.empty()
        current_session.commit()
        CocktailScanCache.invalidate()

        return len(objects), 204


@ns.route('/search')
class CocktailSearchEndpoint(Resource):
    # Amazingly it took finding this post to figure out how
    # this is supposed to work.
    # https://stackoverflow.com/questions/41227736/flask-something-more-strict-than-api-expect-for-input-data
    #
    # An empty body is not valid JSON, so if you try and curl this (or anything that does a RequestParser.parse_args())
    # it will fail with a cryptic way of saying "BAD REQEUST" (HTTP/400) which is considered the appropriate response.
    # This happens whether strict is True or False. You can do something like:
    #   curl -H "Content-Type: application-json" -X GET -d '{}' localhost:8080/api/v1/cocktails/search
    # and you'll get a good response (HTTP/200), but that seems like even more haxx. Note that if you don't do the -X GET
    # curl will infer you meant POST and do that instead, which is not allowed (HTTP/405)
    # https://github.com/pallets/flask/issues/1317
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
        c = CocktailFactory.produce_obj(id=slug)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, slug):
        """
        Delete a single cocktail from the database.
        :param slug:
        :return:
        """
        c = CocktailFactory.produce_obj(id=slug)
        CocktailFactory.delete_obj(obj=c)
        CocktailScanCache.invalidate()
        RecipeIndexer.delete(c)
        return None, 204


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
        serialized_citations = RecipeBibliographyCache.retrieve()
        return json.loads(serialized_citations)


@ns.route('/notebook')
class CocktailNotebookEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(TextItem)
    def get(self):
        return json.loads(NotebookCache.retrieve())
