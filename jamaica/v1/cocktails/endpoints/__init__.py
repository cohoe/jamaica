import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.cocktails.serializers import CocktailSearchItem, CocktailItem
from jamaica.v1.cocktails.parsers import cocktail_list_parser
from flask_sqlalchemy_session import current_session

from barbados.search.cocktail import CocktailSearch
from barbados.caches import CocktailScanCache
from barbados.models import CocktailModel
from barbados.factories import CocktailFactory
from barbados.serializers import ObjectSerializer
from barbados.indexers import indexer_factory
from barbados.validators import ObjectValidator

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
        :raises IntegrityError:
        """
        # Build
        c = CocktailFactory.raw_to_obj(api.payload, api.payload.get('slug'))
        model = CocktailModel(**ObjectSerializer.serialize(c, 'dict'))
        ObjectValidator.validate(model, session=current_session)

        # Write
        current_session.add(model)
        current_session.commit()
        indexer_factory.get_indexer(c).index(c)

        # Invalidate Cache
        CocktailScanCache.invalidate()

        # Return
        return ObjectSerializer.serialize(c, 'dict')


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
        :raises KeyError:
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
        :raises KeyError: Not found
        """
        result = current_session.query(CocktailModel).get(slug)

        if not result:
            raise KeyError('Not found')

        c = CocktailFactory.model_to_obj(result)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, slug):
        """
        Delete a single cocktail from the database.
        :param slug:
        :return:
        :raises KeyError:
        """
        result = current_session.query(CocktailModel).get(slug)
        c = CocktailFactory.model_to_obj(result)

        if not result:
            raise KeyError('Not found')

        current_session.delete(result)
        current_session.commit()

        CocktailScanCache.invalidate()
        indexer_factory.get_indexer(c).delete(c)
