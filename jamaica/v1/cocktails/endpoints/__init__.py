import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.cocktails.serializers import CocktailIndex, CocktailSearchItem, CocktailItem
from jamaica.v1.cocktails.parsers import cocktail_list_parser
from flask_sqlalchemy_session import current_session

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
    @api.response(200, 'success')
    @api.expect(cocktail_list_parser, validate=True)
    @api.marshal_list_with(CocktailSearchItem)
    def get(self):
        """
        Get a simplified view of cocktails from search.
        :return: List of SearchResult Dicts
        :raises KeyError:
        """
        args = cocktail_list_parser.parse_args(strict=True)
        return CocktailSearch(**args).execute()

    @api.response(200, 'success')
    @api.expect(CocktailItem, validate=True)
    @api.marshal_list_with(CocktailItem)
    def post(self):
        """
        Create a new cocktail.
        :return: Serialized Cocktail object.
        :raises IntegrityError:
        """
        c = CocktailFactory.raw_to_obj(api.payload, api.payload.get('slug'))
        db_obj = CocktailModel(**ObjectSerializer.serialize(c, 'dict'))
        current_session.add(db_obj)
        current_session.commit()
        return ObjectSerializer.serialize(c, 'dict')


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

        if not result:
            raise KeyError('Not found')

        current_session.delete(result)
        current_session.commit()


@ns.route('/index')
class CocktailIndexEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(CocktailIndex)
    def get(self):
        """
        Get a simplified list of all cocktails from cache.
        :return: List
        """
        return json.loads(CocktailNameCache.retrieve())
