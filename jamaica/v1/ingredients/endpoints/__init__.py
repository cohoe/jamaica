import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.ingredients.serializers import IngredientIndexItem, IngredientObject, IngredientSearchItem, IngredientSubstitution
from jamaica.v1.ingredients.parsers import ingredient_list_parser
from flask_sqlalchemy_session import current_session

from barbados.search.ingredient import IngredientSearch
from barbados.caches import IngredientTreeCache, UsableIngredientCache
from barbados.models import IngredientModel
from barbados.factories import IngredientFactory
from barbados.serializers import ObjectSerializer

ns = api.namespace('v1/ingredients', description='Ingredients.')


@ns.route('/')
class IngredientsEndpoint(Resource):

    @api.response(200, 'success')
    @api.expect(ingredient_list_parser, validate=True)
    @api.marshal_list_with(IngredientSearchItem)
    def get(self):
        """
        Lookup ingredients in search.
        :return: List of search result Dicts
        """
        args = ingredient_list_parser.parse_args(strict=True)
        return IngredientSearch(**args).execute()


@ns.route('/index')
class IngredientIndexEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(IngredientIndexItem)
    def get(self):
        """
        Simplified list of ingredients from cache rather than search.
        """
        return json.loads(UsableIngredientCache.retrieve())


@ns.route('/tree')
class IngredientTreeEndpoint(Resource):

    @api.response(200, 'success')
    # @TODO Nothing here works. Recursion with models is really lacking...
    # @api.marshal_with(ingredient_tree_model)
    def get(self):
        """
        Get the entire ingredient tree from cache.
        :return: Dict
        """
        ingredient_tree = IngredientTreeCache.retrieve()
        return json.loads(ingredient_tree.tree.to_json(with_data=True))


@ns.route('/<string:slug>')
@api.doc(params={'slug': 'An ingredient slug.'})
class IngredientEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(IngredientObject)
    def get(self, slug):
        """
        Get a single ingredient from the database.
        :param slug:
        :return: Serialized Ingredient
        :raises KeyError: not found
        """
        result = current_session.query(IngredientModel).get(slug)
        c = IngredientFactory.model_to_obj(result)
        return ObjectSerializer.serialize(c, 'dict')


@ns.route('/<string:slug>/subtree')
class IngredientSubtreeEndpoint(Resource):

    # @TODO when you figure out recursive tree modeling, call here.
    @api.response(200, 'success')
    def get(self, slug):
        """
        Return the subtree of this ingredient from the main tree.
        :param slug:
        :return: Dict
        :raises KeyError: not found
        """
        ingredient_tree = IngredientTreeCache.retrieve()
        return json.loads(ingredient_tree.subtree(slug).to_json(with_data=True))


@ns.route('/<string:slug>/substitution')
class IngredientSubstitutionEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(IngredientSubstitution)
    def get(self, slug):
        """
        Return relevant information needed to substitute this ingredient.
        :param slug:
        :return: Dict
        :raises KeyError: not found
        """
        ingredient_tree = IngredientTreeCache.retrieve()
        return ingredient_tree.substitutions(slug)
