import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.ingredients.serializers import IngredientObject, IngredientSearchItem, IngredientSubstitution
from jamaica.v1.ingredients.parsers import ingredient_list_parser
from flask_sqlalchemy_session import current_session

from barbados.search.ingredient import IngredientSearch
from barbados.caches import IngredientTreeCache, IngredientScanCache
from barbados.models import IngredientModel
from barbados.factories import IngredientFactory
from barbados.serializers import ObjectSerializer

ns = api.namespace('v1/ingredients', description='Ingredient database.')


@ns.route('/')
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
    @api.expect([IngredientObject], validate=True)
    @api.marshal_list_with(IngredientObject)
    def post(self):
        """
        Create a new set of ingredients.
        :return: List of the ingredients you created.
        :raises IntegrityError:
        """
        serialized_objects = []
        for raw_ingredient in api.payload:
            i = IngredientFactory.raw_to_obj(raw_ingredient)
            ser_i = ObjectSerializer.serialize(i, 'dict')
            serialized_objects.append(ser_i)
            current_session.add(IngredientModel(**ser_i))

        current_session.commit()
        IngredientScanCache.invalidate()
        return serialized_objects


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

    @api.response(204, 'successful delete')
    def delete(self, slug):
        """
        Delete a single ingredient from the database.
        :param slug:
        :return:
        :raises KeyError:
        """
        result = current_session.query(IngredientModel).get(slug)

        if not result:
            raise KeyError('Not found')

        current_session.delete(result)
        current_session.commit()


@ns.route('/<string:slug>/subtree')
class IngredientSubtreeEndpoint(Resource):

    @api.response(200, 'success')
    def get(self, slug):
        """
        Return the subtree of this ingredient from the main tree.
        No api.marshal_with() due to recursion.
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
