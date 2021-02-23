from flask_restx import Resource
from jamaica.v1.restx import api
from flask_sqlalchemy_session import current_session

from jamaica.v1.serializers import ConstructionItem

from barbados.caches.tablescan import ConstructionScanCache
from barbados.factories.construction import ConstructionFactory
from barbados.serializers import ObjectSerializer


ns = api.namespace('v1/constructions', description='Construction methods.')


@ns.route('')
class ConstructionsEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(ConstructionItem)
    def get(self):
        """
        List all Constructions.
        :return: List of serialized Construction objects.
        """
        return ConstructionScanCache.retrieve()

    @api.response(201, 'created')
    @api.expect(ConstructionItem, validate=True)
    @api.marshal_with(ConstructionItem)
    def post(self):
        """
        Insert new Construction.
        :return: Serialized Construction object.
        """
        c = ConstructionFactory.raw_to_obj(api.payload)
        ConstructionFactory.insert_obj(obj=c)
        ConstructionScanCache.invalidate()
        return ObjectSerializer.serialize(c, 'dict'), 201

    @api.response(204, 'successful delete')
    def delete(self):
        """
        Delete all Constructions.
        :return: Count of deleted objects.
        """
        objs = [ConstructionFactory.raw_to_obj(construction) for construction in ConstructionScanCache.retrieve()]
        for c in objs:
            ConstructionFactory.delete_obj(c, commit=False)
        current_session.commit()
        ConstructionScanCache.invalidate()
        return len(objs), 204


@ns.route('/<string:slug>')
@api.doc(params={'slug': 'A construction slug.'})
class ConstructionEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(ConstructionItem)
    def get(self, slug):
        """
        Get a Construction.
        :param slug: Construction slug.
        :return: Serialized Construction object.
        """
        c = ConstructionFactory.produce_obj(id=slug)
        return ObjectSerializer.serialize(c, 'dict')

    @api.expect(ConstructionItem, validate=True)
    @api.marshal_with(ConstructionItem)
    @api.response(200, 'success')
    def post(self, slug):
        """
        Update a Construction.
        :param slug: Construction slug.
        :return: Serialized Construction object.
        """
        c = ConstructionFactory.raw_to_obj(api.payload)
        ConstructionFactory.update_obj(obj=c, id_value=slug)
        ConstructionScanCache.invalidate()
        return ObjectSerializer.serialize(c, 'dict'), 200

    @api.response(204, 'successful delete')
    def delete(self, slug):
        """
        Delete a Construction.
        :param slug: Construction slug.
        :return: None
        """
        c = ConstructionFactory.produce_obj(id=slug)
        ConstructionFactory.delete_obj(c)
        ConstructionScanCache.invalidate()
        return None, 204
