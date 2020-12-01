import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.inventories.serializers import InventoryObject
# from jamaica.v1.inventories.parsers import menu_list_parser
from flask_sqlalchemy_session import current_session

from barbados.models import InventoryModel
from barbados.factories import InventoryFactory
from barbados.serializers import ObjectSerializer
from barbados.caches import InventoryScanCache, IngredientTreeCache
from barbados.indexers import indexer_factory
from barbados.search.menu import MenuSearch
from barbados.validators import ObjectValidator

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
        f = InventoryFactory.raw_to_obj(api.payload)
        model = InventoryModel(**ObjectSerializer.serialize(f, 'dict'))
        ObjectValidator.validate(model, session=current_session)

        current_session.add(model)
        current_session.commit()
        # @TODO index inventories?
        # indexer_factory.get_indexer(m).index(m)

        # Invalidate Cache
        InventoryScanCache.invalidate()

        return ObjectSerializer.serialize(f, 'dict')

    @api.response(204, 'successful delete')
    def delete(self):
        """
        Delete all objects from the database. There be dragons here.
        :return: Number of items deleted.
        """
        results = current_session.query(InventoryModel).all()
        for result in results:
            i = InventoryFactory.model_to_obj(result)
            current_session.delete(result)
            # @TODO indexes
            # indexer_factory.get_indexer(i).delete(i)

        current_session.commit()
        InventoryScanCache.invalidate()

        return len(results)


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
        result = current_session.query(InventoryModel).get(id)
        c = InventoryFactory.model_to_obj(result)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, id):
        """
        Delete a single object from the database.
        :param id: GUID of the object.
        :return: None
        :raises KeyError:
        """
        result = current_session.query(InventoryModel).get(id)
        i = InventoryFactory.model_to_obj(result)

        if not result:
            raise KeyError('Not found')

        current_session.delete(result)
        current_session.commit()

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
        result = current_session.query(InventoryModel).get(id)
        c = InventoryFactory.model_to_obj(result)
        # @TODO until dev is done
        # tree = IngredientTreeCache.retrieve()
        from barbados.objects.ingredienttree import IngredientTree
        tree = IngredientTree()

        c.full(tree=tree)

        return ObjectSerializer.serialize(c, 'dict')
