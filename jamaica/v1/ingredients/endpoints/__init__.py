import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.ingredients.serializers import IngredientObject, IngredientSearchItem, IngredientSubstitution
from jamaica.v1.ingredients.parsers import ingredient_list_parser
from flask_sqlalchemy_session import current_session

from barbados.search.ingredient import IngredientSearch
from barbados.caches.ingredienttree import IngredientTreeCache
from barbados.caches.tablescan import IngredientScanCache
from barbados.factories.ingredient import IngredientFactory
from barbados.serializers import ObjectSerializer
from barbados.indexers.ingredient import IngredientIndexer

ns = api.namespace('v1/ingredients', description='Ingredient database.')


@ns.route('')
class IngredientsEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(IngredientObject)
    def get(self):
        """
        List all ingredients
        :return: List of Ingredient dicts
        """
        serialized_ingredients = json.loads(IngredientScanCache.retrieve())
        return serialized_ingredients

    @api.response(200, 'success')
    @api.expect(IngredientObject, validate=True)
    @api.marshal_with(IngredientObject)
    def post(self):
        """
        Create a new ingredient.
        :return: Ingredient you created.
        """
        i = IngredientFactory.raw_to_obj(api.payload)
        i.refresh()
        IngredientFactory.store_obj(obj=i)
        IngredientIndexer.index(i)

        # Invalidate cache
        IngredientScanCache.invalidate()
        IngredientTreeCache.invalidate()

        return ObjectSerializer.serialize(i, 'dict')

    @api.response(204, 'successful delete')
    def delete(self):
        """
        Delete all ingredients from the database. There be dragons here.
        :return: Number of items deleted.
        """
        objects = IngredientFactory.produce_all_objs()
        for i in objects:
            IngredientFactory.delete_obj(obj=i, commit=False)

        IngredientIndexer.empty()

        current_session.commit()
        IngredientScanCache.invalidate()
        IngredientTreeCache.invalidate()

        return len(objects)


@ns.route('/search')
class IngredientSearchEndpoint(Resource):

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


@ns.route('/tree')
class IngredientTreeEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Get the entire ingredient tree from cache. No marshaling model
        is documented due to recursion problems.
        :return: Dict
        """
        ingredient_tree = IngredientTreeCache.retrieve()
        return json.loads(ingredient_tree.to_json())


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
        """
        c = IngredientFactory.produce_obj(id=slug)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, slug):
        """
        Delete a single ingredient from the database.
        :param slug:
        :return:
        """
        i = IngredientFactory.produce_obj(id=slug)
        IngredientFactory.delete_obj(obj=i)

        # Invalidate caches and de-index.
        IngredientScanCache.invalidate()
        IngredientTreeCache.invalidate()
        IngredientIndexer.delete(i)


@ns.route('/<string:slug>/subtree')
class IngredientSubtreeEndpoint(Resource):

    @api.response(200, 'success')
    def get(self, slug):
        """
        Return the subtree of this ingredient from the main tree.
        No api.marshal_with() due to recursion.
        :param slug:
        :return: Dict
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
        """
        ingredient_tree = IngredientTreeCache.retrieve()
        return ingredient_tree.substitutions(slug)


@ns.route('/<string:slug>/refresh')
class IngredientRefreshEndpoint(Resource):

    @api.response(200, 'success')
    def post(self, slug):
        """
        Refresh an ingredient that supports refreshing.
        :param slug:
        :return: None
        """
        i = IngredientFactory.produce_obj(id=slug)
        i.refresh()
        IngredientFactory.update_obj(obj=i)
        IngredientIndexer.index(i)

        # Invalidate cache
        IngredientScanCache.invalidate()
