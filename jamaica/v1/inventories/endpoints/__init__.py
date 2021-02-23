from flask_restx import Resource
from jamaica.cache import flask_cache
from jamaica.v1.restx import api
from jamaica.v1.inventories.serializers import InventoryObject
from jamaica.v1.inventories.parsers import inventory_recipes_parser
from jamaica.v1.inventories.serializers import InventoryResolutionSummaryObject, InventoryItemObject
from flask_sqlalchemy_session import current_session

from barbados.factories.inventory import InventoryFactory
from barbados.factories.cocktail import CocktailFactory
from barbados.factories.reciperesolution import RecipeResolutionFactory
from barbados.serializers import ObjectSerializer
from barbados.caches.tablescan import InventoryScanCache
from barbados.resolvers.recipe import RecipeResolver
from barbados.caches.tablescan import CocktailScanCache
from barbados.search.reciperesolution import RecipeResolutionSearch
from barbados.indexers.reciperesolution import RecipeResolutionIndexer
from barbados.indexers.inventory import InventoryIndexer
from barbados.reports.inventory import InventoryReport


ns = api.namespace('v1/inventories', description='Inventories.')


@ns.route('')
class InventoriesEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(InventoryObject)
    def get(self):
        """
        List all Inventories
        :return: List of Inventory dicts
        """
        serialized_objects = InventoryScanCache.retrieve()
        return serialized_objects

    @api.response(201, 'created')
    @api.expect(InventoryObject, validate=True)
    @api.marshal_with(InventoryObject)
    def post(self):
        """
        Create a new object.
        :return: Object that you created.
        :raises IntegrityError:
        """
        # https://stackoverflow.com/questions/11277432/how-can-i-remove-a-key-from-a-python-dictionary
        api.payload.pop('id', None)
        i = InventoryFactory.raw_to_obj(api.payload)
        InventoryFactory.insert_obj(obj=i)

        # Index
        InventoryIndexer.index(i)

        # Invalidate Cache
        InventoryScanCache.invalidate()

        return ObjectSerializer.serialize(i, 'dict'), 201

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

        InventoryIndexer.empty()
        InventoryScanCache.invalidate()

        return len(objects), 204


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
        InventoryIndexer.delete(i)

        return None, 204


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
        InventoryIndexer.index(i)
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


@ns.route('/<uuid:id>/recipes/<string:cocktail_slug>')
@ns.route('/<uuid:id>/recipes/<string:cocktail_slug>/<string:spec_slug>')
@api.doc(params={'id': 'Inventory ID object.'})
class InventoryRecipeEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(InventoryResolutionSummaryObject)
    def get(self, id, cocktail_slug, spec_slug=None):
        """
        :param id:
        :param cocktail_slug:
        :param spec_slug:
        :return:
        """
        i = InventoryFactory.produce_obj(id=id)

        c = CocktailFactory.produce_obj(id=cocktail_slug)
        results = RecipeResolver.resolve(inventory=i, cocktail=c, spec_slug=spec_slug)

        # Save the things we got.
        [RecipeResolutionFactory.insert_obj(rs, overwrite=True) for rs in results]
        [RecipeResolutionIndexer.index(rs) for rs in results]

        return [ObjectSerializer.serialize(rs, 'dict') for rs in results]

    @api.response(204, 'successful delete')
    def delete(self, id, cocktail_slug, spec_slug=None):
        """
        :param id:
        :param cocktail_slug:
        :param spec_slug:
        :return:
        """
        i = InventoryFactory.produce_obj(id=id)

        c = CocktailFactory.produce_obj(id=cocktail_slug)
        results = RecipeResolver.resolve(inventory=i, cocktail=c, spec_slug=spec_slug)

        # Drop
        [RecipeResolutionFactory.delete_obj(rs) for rs in results]
        [RecipeResolutionIndexer.index(rs) for rs in results]

        return None, 204


@ns.route('/<uuid:id>/recipes')
@api.doc(params={'id': 'Inventory ID object.'})
class InventoryRecipesEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(InventoryResolutionSummaryObject)
    @flask_cache.cached()
    def get(self, id):
        """
        :param id:
        :return:
        """
        i = InventoryFactory.produce_obj(id=id)

        results = []
        cocktails_cache = CocktailScanCache.retrieve()
        for raw_c in cocktails_cache:
            c = CocktailFactory.produce_obj(id=raw_c.get('slug'))
            c_results = RecipeResolver.resolve(inventory=i, cocktail=c)
            results += c_results

        # Save the things we got.
        [RecipeResolutionFactory.insert_obj(rs, overwrite=True) for rs in results]
        [RecipeResolutionIndexer.index(rs) for rs in results]

        return [ObjectSerializer.serialize(rs, 'dict') for rs in results]

    @api.response(204, 'successful delete')
    def delete(self, id):
        """
        Delete all recipe resolutions for this inventory
        :param id: Inventory ID UUID
        :return: Count of deletions.
        """
        results = RecipeResolutionFactory.produce_all_objs_from_inventory(inventory_id=id)
        for rs in results:
            RecipeResolutionFactory.delete_obj(rs, commit=False)
        current_session.commit()

        return len(results), 204


@ns.route('/<uuid:id>/recipes/search')
@api.doc(params={'id': 'An object ID.'})
class InventoryRecipesEndpoint(Resource):

    def get(self, id):
        inventory_recipes_parser.add_argument('inventory_id', default=str(id))
        args = inventory_recipes_parser.parse_args(strict=True)

        # Don't return any results if all parameters are empty.
        # https://stackoverflow.com/questions/35253971/how-to-check-if-all-values-of-a-dictionary-are-0
        if all(value is None for value in args.values()):
            return []

        return RecipeResolutionSearch(**args).execute()


@ns.route('/<uuid:id>/report')
@api.doc(params={'id': 'An object ID.'})
class InventoryReportEndpoint(Resource):

    def get(self, id):
        i = InventoryFactory.produce_obj(id=id)
        r = InventoryReport(inventory=i)
        return r.run()
