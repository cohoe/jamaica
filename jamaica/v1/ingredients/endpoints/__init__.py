import json
from flask import request
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.ingredients.serializers import ingredient_list_result, ingredient_search_index, ingredient_substitution
from jamaica.v1.ingredients.parsers import ingredient_list_parser

from barbados.search.ingredient import IngredientSearch
from barbados.caches import IngredientTreeCache, UsableIngredientCache
from barbados.models import IngredientModel
from barbados.factories import IngredientFactory
from barbados.serializers import ObjectSerializer

ns = api.namespace('v1/ingredients', description='Ingredients.')


@ns.route('/')
class IngredientCollection(Resource):

    @api.expect(ingredient_list_parser, validate=True) # @TODO validate doesnt work.
    @api.marshal_list_with(ingredient_list_result)
    def get(self):
        """
        Lookup ingredients in search.
        :return: List of search result Dicts
        """
        return IngredientSearch(**request.args).execute()


@ns.route('/index')
class IngredientIndexItem(Resource):

    @api.marshal_list_with(ingredient_search_index)
    def get(self):
        """
        Simplified list of ingredients from cache rather than search.
        """
        return json.loads(UsableIngredientCache.retrieve())


@ns.route('/tree')
class IngredientTreeItem(Resource):

    # @api.marshal_with(Ingredient_search_index)
    def get(self):
        """
        Get the entire ingredient tree from cache.
        :return: Dict
        """
        ingredient_tree = IngredientTreeCache.retrieve()
        return ingredient_tree.tree.to_json(with_data=True)


@ns.route('/<string:slug>')
@api.response(404, 'Ingredient slug not in database.')
@api.doc(params={'slug': 'An ingredient slug.'})
class IngredientItem(Resource):

    def get(self, slug):
        """
        Get a single ingredient from the database.
        :param slug:
        :return: Serialized Ingredient
        """
        try:
            result = IngredientModel.get_by_slug(slug)
            c = IngredientFactory.model_to_obj(result)
            return ObjectSerializer.serialize(c, 'dict')
        except KeyError:
            ns.abort(404, 'Ingredient not found.', slug=slug)


@ns.route('/<string:slug>/subtree')
@api.response(404, 'Ingredient slug not in database.')
class IngredientSubtreeItem(Resource):

    def get(self, slug):
        """
        Return the subtree of this ingredient from the main tree.
        :param slug:
        :return: Dict
        """
        try:
            ingredient_tree = IngredientTreeCache.retrieve()
            return json.loads(ingredient_tree.subtree(slug).to_json(with_data=True))
        except KeyError:
            ns.abort(404, 'Ingredient not found.', slug=slug)


@ns.route('/<string:slug>/parents')
@api.response(404, 'Ingredient slug not in database.')
class IngredientParentItem(Resource):

    def get(self, slug):
        """
        @TODO DEPRECATE THIS SHIT
        Get a list of the slugs of every parent of this ingredient. These go all the way
        to the root of the tree.
        :param slug:
        :return: List of Strings
        """
        try:
            ingredient_tree = IngredientTreeCache.retrieve()
            parents = ingredient_tree.parents(slug)

            return parents
        except KeyError:
            ns.abort(404, 'Ingredient not found.', slug=slug)


@ns.route('/<string:slug>/substitutions')
@api.response(404, 'Ingredient slug not in database.')
class IngredientSubstitutionsItem(Resource):

    @api.marshal_with(ingredient_substitution)
    def get(self, slug):
        """
        Return relevant information needed to substitute this ingredient.
        :param slug:
        :return: Dict
        """
        try:
            ingredient_tree = IngredientTreeCache.retrieve()
            return ingredient_tree.substitutions(slug)
        except KeyError:
            ns.abort(404, 'Ingredient not found.', slug=slug)
