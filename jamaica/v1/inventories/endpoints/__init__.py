import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.inventories.serializers import InventoryObject
from jamaica.v1.inventories.parsers import inventory_recipes_parser
from jamaica.v1.inventories.serializers import InventoryResolutionSummaryObject, InventoryItemObject
from flask_sqlalchemy_session import current_session

from barbados.factories.inventoryfactory import InventoryFactory
from barbados.factories.cocktailfactory import CocktailFactory
from barbados.serializers import ObjectSerializer
from barbados.caches.tablescan import InventoryScanCache
from barbados.resolvers.recipe import RecipeResolver
from barbados.caches.tablescan import CocktailScanCache
from barbados.search.inventoryspecresolution import InventorySpecResolutionSearch


ns = api.namespace('v1/inventories', description='Inventories.')


@ns.route('/')
class InventoriesEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(InventoryObject)
    def get(self):
        """
        List all Inventories
        :return: List of Inventory dicts
        """
        serialized_objects = json.loads(InventoryScanCache.retrieve())
        return serialized_objects

    @api.response(200, 'success')
    @api.expect(InventoryObject, validate=True)
    @api.marshal_with(InventoryObject)
    def post(self):
        """
        Create a new object.
        :return: Object that you created.
        :raises IntegrityError:
        """
        i = InventoryFactory.raw_to_obj(api.payload)
        InventoryFactory.store_obj(obj=i)

        # @TODO index inventories?
        # indexer_factory.get_indexer(m).index(m)

        # Invalidate Cache
        InventoryScanCache.invalidate()

        return ObjectSerializer.serialize(i, 'dict')

    @api.response(204, 'successful delete')
    def delete(self):
        """
        Delete all objects from the database. There be dragons here.
        :return: Number of items deleted.
        """

        objects = InventoryFactory.produce_all_objs()
        for i in objects:
            InventoryFactory.delete_obj(obj=i, commit=False)

        current_session.commit()

        # @TODO indexes
        # InventoryIndexer.empty()
        InventoryScanCache.invalidate()

        return len(objects)


@ns.route('/<uuid:id>')
@api.doc(params={'id': 'An object ID.'})
class InventoryEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(InventoryObject)
    def get(self, id):
        """
        Get a single object from the database.
        :param id: GUID of the object.
        :return: Serialized Object
        :raises KeyError: not found
        """
        c = InventoryFactory.produce_obj(id=id)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, id):
        """
        Delete a single object from the database.
        :param id: GUID of the object.
        :return: None
        :raises KeyError: not found
        """
        i = InventoryFactory.produce_obj(id=id)
        InventoryFactory.delete_obj(obj=i)

        # Invalidate Cache
        InventoryScanCache.invalidate()
        # @TODO this
        # indexer_factory.get_indexer(i).delete(i)


@ns.route('/<uuid:id>/full')
@api.doc(params={'id': 'An object ID.'})
class InventoryFullEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(InventoryObject)
    def get(self, id):
        """
        Return a fully-expanded inventory including the implicitly
        included items.
        :param id: GUID of the object.
        :return: Serialized Object
        :raises KeyError: not found
        """
        i = InventoryFactory.produce_obj(id=id, expand=True)
        return ObjectSerializer.serialize(i, 'dict')


@ns.route('/<uuid:id>/items/<string:slug>')
@api.doc(params={
    'id': 'An inventory ID',
    'slug': 'An item slug'
})
class InventoryItemsEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(InventoryItemObject)
    def get(self, id, slug):
        """
        Return a single inventory item.
        :param id: GUID of the inventory.
        :param slug: Slug of the item.
        :return: InventoryItem
        """
        i = InventoryFactory.produce_obj(id=id, expand=True)
        ii = i.items.get(slug)

        if not ii:
            raise KeyError("Item %s not found in inventory %s." % (slug, id))

        return ObjectSerializer.serialize(ii, 'dict')


@ns.route('/<uuid:id>/recipes')
@ns.route('/<uuid:id>/recipes/<string:cocktail_slug>')
@ns.route('/<uuid:id>/recipes/<string:cocktail_slug>/<string:spec_slug>')
@api.doc(params={'id': 'An object ID.'})
class InventoryRecipesEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(InventoryResolutionSummaryObject)
    def get(self, id, cocktail_slug=None, spec_slug=None):
        """
        :param id:
        :param cocktail_slug:
        :param spec_slug:
        :return:
        """
        i = InventoryFactory.produce_obj(id=id)

        results = []
        if cocktail_slug:
            c = CocktailFactory.produce_obj(id=cocktail_slug)
            results = RecipeResolver.resolve(inventory=i, cocktail=c, spec_slug=spec_slug)
        else:
            # @TODO fetch from cache for RecipeResolver
            cocktails_cache = CocktailScanCache.retrieve()
            for raw_c in json.loads(cocktails_cache):
                c = CocktailFactory.produce_obj(id=raw_c.get('slug'))
                c_results = RecipeResolver.resolve(inventory=i, cocktail=c)
                results += c_results

        return [ObjectSerializer.serialize(rs, 'dict') for rs in results]


@ns.route('/<uuid:id>/recipes/search')
@api.doc(params={'id': 'An object ID.'})
class InventoryRecipesEndpoint(Resource):

    def get(self, id):
        # @TODO ponder a better way to do this. It can't go in the parser itself because
        # that lets end users specify their own value.
        inventory_recipes_parser.add_argument('inventory_id', default=str(id))
        args = inventory_recipes_parser.parse_args(strict=True)

        # Don't return any results if all parameters are empty.
        # https://stackoverflow.com/questions/35253971/how-to-check-if-all-values-of-a-dictionary-are-0
        if all(value is None for value in args.values()):
            return []

        return InventorySpecResolutionSearch(**args).execute()
