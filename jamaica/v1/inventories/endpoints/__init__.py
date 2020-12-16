import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.inventories.serializers import InventoryObject
from jamaica.v1.serializers import CocktailSearchItem
from jamaica.v1.inventories.parsers import inventory_resolve_parser, inventory_recipes_parser
from jamaica.v1.inventories.serializers import InventoryResolutionSummaryObject, InventoryItemObject
from flask_sqlalchemy_session import current_session

from barbados.factories.inventoryfactory import InventoryFactory
from barbados.factories.cocktailfactory import CocktailFactory
from barbados.serializers import ObjectSerializer
from barbados.caches.tablescan import InventoryScanCache
from barbados.resolvers.reciperesolver import RecipeResolver
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
        InventoryFactory.store_obj(session=current_session, obj=i)

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

        objects = InventoryFactory.produce_all_objs(session=current_session)
        for i in objects:
            InventoryFactory.delete_obj(session=current_session, obj=i, commit=False)

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
        c = InventoryFactory.produce_obj(session=current_session, id=id)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, id):
        """
        Delete a single object from the database.
        :param id: GUID of the object.
        :return: None
        :raises KeyError: not found
        """
        i = InventoryFactory.produce_obj(session=current_session, id=id)
        InventoryFactory.delete_obj(session=current_session, obj=i)

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
        i = InventoryFactory.produce_obj(session=current_session, id=id, expand=True)
        return ObjectSerializer.serialize(i, 'dict')


@ns.route('/<uuid:id>/recipes')
@api.doc(params={'id': 'An object ID.'})
class InventoryRecipesEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(InventoryResolutionSummaryObject)
    def get(self, id):
        """
        @TODO this, something?
        :param id:
        :return:
        """
        i = InventoryFactory.produce_obj(session=current_session, id=id)
        cocktails_cache = CocktailScanCache.retrieve()

        results = []
        for raw_c in json.loads(cocktails_cache):
            c = CocktailFactory.produce_obj(session=current_session, id=raw_c.get('slug'))
            c_results = RecipeResolver.resolve(inventory=i, cocktail=c)
            results += c_results

        return [ObjectSerializer.serialize(rs, 'dict') for rs in results]


@ns.route('/<uuid:id>/recipes/search')
@api.doc(params={'id': 'An object ID.'})
class InventoryRecipesEndpoint(Resource):

    def get(self, id):
        # @TODO id
        args = inventory_recipes_parser.parse_args(strict=True)

        # Don't return any results if all parameters are empty.
        # https://stackoverflow.com/questions/35253971/how-to-check-if-all-values-of-a-dictionary-are-0
        if all(value is None for value in args.values()):
            return []

        return InventorySpecResolutionSearch(**args).execute()


@ns.route('/<uuid:id>/resolve')
@api.doc(params={'id': 'An object ID.'})
class InventoryResolveEndpoint(Resource):

    @api.response(200, 'success')
    @api.expect(inventory_resolve_parser, validate=True)
    @api.marshal_list_with(InventoryResolutionSummaryObject)
    def get(self, id):
        """
        :param id: GUID of the object.
        """
        args = inventory_resolve_parser.parse_args(strict=True)

        # Don't return any results if all parameters are empty.
        # https://stackoverflow.com/questions/35253971/how-to-check-if-all-values-of-a-dictionary-are-0
        if all(value is None for value in args.values()):
            return []

        i = InventoryFactory.produce_obj(session=current_session, id=id)

        results = []
        if args.cocktail:
            c = CocktailFactory.produce_obj(session=current_session, id=args.cocktail)
            results = RecipeResolver.resolve(inventory=i, cocktail=c, spec_slug=args.spec)

        return [ObjectSerializer.serialize(rs, 'dict') for rs in results]


@ns.route('/<uuid:id>/item/<string:slug>')
@api.doc(params={
    'id': 'An inventory ID',
    'slug': 'An item slug'
})
class InventoryItemEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(InventoryItemObject)
    def get(self, id, slug):
        """
        Return a single inventory item.
        :param id: GUID of the inventory.
        :param slug: Slug of the item.
        :return: InventoryItem
        """
        i = InventoryFactory.produce_obj(session=current_session, id=id, expand=True)
        ii = i.items.get(slug)

        if not ii:
            raise KeyError("Item %s not found in inventory %s." % (slug, id))

        return ObjectSerializer.serialize(ii, 'dict')
