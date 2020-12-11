import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.inventories.serializers import InventoryObject
from jamaica.v1.serializers import CocktailSearchItem
from jamaica.v1.inventories.parsers import inventory_resolve_parser
from jamaica.v1.inventories.serializers import InventoryResolutionSummaryObject
from flask_sqlalchemy_session import current_session

from barbados.factories import InventoryFactory, CocktailFactory
from barbados.serializers import ObjectSerializer
from barbados.caches import InventoryScanCache, IngredientTreeCache
from barbados.search.cocktail import CocktailSearch
from barbados.services.logging import Log
from barbados.resolvers.reciperesolver import RecipeResolver


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
        i = InventoryFactory.produce_obj(session=current_session, id=id)
        # @TODO until dev is done
        # tree = IngredientTreeCache.retrieve()
        from barbados.objects.ingredienttree import IngredientTree
        tree = IngredientTree()

        i.expand(tree=tree)

        return ObjectSerializer.serialize(i, 'dict')


@ns.route('/<uuid:id>/recipes')
@api.doc(params={'id': 'An object ID.'})
class InventoryRecipesEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(CocktailSearchItem)
    def get(self, id):
        """
        Return a list of all recipes that this inventory can make.
        # @TODO parameter for tolerance to find things that are missing n.
        :param id: GUID of the object.
        """
        recipes = []

        i = InventoryFactory.produce_obj(session=current_session, id=id)
        i.full(tree=IngredientTreeCache.retrieve())

        inventory_item_slugs = []
        for inventory_item in i.items:
            inventory_item_slugs.append(inventory_item.slug)
            # print(inventory_item.slug)
            recipe_search_results = CocktailSearch(components=[inventory_item.slug]).execute()
            recipes += recipe_search_results

        Log.info("This inventory contains: %s" % inventory_item_slugs)

        # CocktailSearch(**args).execute()
        accepted_results = []
        # print(len(recipe_search_results))
        for result in recipe_search_results:
            # print(list(result.keys()))

            component_status = {}

            for spec_component in result.get('hit').get('spec').get('components'):
                #print(spec_component.get('slug'))
                # Check if we have the specified ingredient
                spec_component_slug = spec_component.get('slug')

                # Establish baseline status of not-found.
                component_status[spec_component_slug] = None

                if spec_component_slug in inventory_item_slugs:
                    # Log.info("Match on %s" % spec_component_slug)
                    component_status[spec_component_slug] = 'DIRECT'
                else:
                    # Log.info("Failed on %s" % spec_component.get('slug'))
                    for spec_component_parent in spec_component.get('parents'):
                        if spec_component_parent in inventory_item_slugs:
                            # Log.info("Match on %s" % spec_component_parent)
                            component_status[spec_component_slug] = 'IMPLIED'

            # print(component_status)
            if None in component_status.values():
                # Log.error("Failed inventory for %s" % result)
                continue

            accepted_results.append(result)

        return accepted_results


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
        if args.recipe:
            c = CocktailFactory.produce_obj(session=current_session, id=args.recipe)
            results = RecipeResolver.resolve(inventory=i, cocktail=c, spec_slug=args.spec)

        return [ObjectSerializer.serialize(rs, 'dict') for rs in results]
