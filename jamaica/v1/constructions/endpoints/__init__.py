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
        Return a list of all constructions.
        :return: List[Dict]
        """
        serialized_constructions = ConstructionScanCache.retrieve()
        return serialized_constructions

    @api.response(200, 'success')
    @api.expect(ConstructionItem, validate=True)
    @api.marshal_with(ConstructionItem)
    def post(self):
        """
        Create a new construction.
        :return: Serialized Construction object.
        """
        c = ConstructionFactory.raw_to_obj(api.payload)
        ConstructionFactory.insert_obj(obj=c)

        # Invalidate Cache
        ConstructionScanCache.invalidate()

        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self):
        """
        Delete all constructions from the database.
        :return: None
        """
        serialized_constructions = ConstructionScanCache.retrieve()
        objs = [ConstructionFactory.raw_to_obj(construction) for construction in serialized_constructions]
        for c in objs:
            ConstructionFactory.delete_obj(c, commit=False)

        current_session.commit()
        ConstructionScanCache.invalidate()
        return len(objs), 204


@ns.route('/<string:slug>')
@api.doc(params={'slug': 'A construction slug.'})
class ConstructionEndpoint(Resource):

    @api.response(200, 'success')
    def get(self, slug):
        """
        Get a construction.
        :param slug: Construction slug
        :return: Serialized Construction object
        """
        c = ConstructionFactory.produce_obj(id=slug)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, slug):
        """
        Delete a construction from the database.
        :param slug: Slug of a construction
        :return: None
        """
        c = ConstructionFactory.produce_obj(id=slug)
        ConstructionFactory.delete_obj(c)
        ConstructionScanCache.invalidate()
        return None, 204
