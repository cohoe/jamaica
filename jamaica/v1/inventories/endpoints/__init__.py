import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.inventories.serializers import InventoryObject
# from jamaica.v1.inventories.parsers import menu_list_parser
from flask_sqlalchemy_session import current_session

from barbados.factories import InventoryFactory
from barbados.serializers import ObjectSerializer
from barbados.caches import InventoryScanCache, IngredientTreeCache


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

        i.full(tree=tree)

        return ObjectSerializer.serialize(i, 'dict')
