from flask_restx import Resource
from jamaica.v1.restx import api
from flask_sqlalchemy_session import current_session

from jamaica.v1.serializers import GlasswareItem

from barbados.caches.tablescan import GlasswareScanCache
from barbados.factories.glassware import GlasswareFactory
from barbados.serializers import ObjectSerializer


ns = api.namespace('v1/glassware', description='Glassware.')


@ns.route('')
class GlasswaresEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(GlasswareItem)
    def get(self):
        """
        Return a list of all glassware.
        :return: List[Dict]
        """
        serialized_glassware = GlasswareScanCache.retrieve()
        return serialized_glassware

    @api.response(201, 'created')
    @api.expect(GlasswareItem, validate=True)
    @api.marshal_with(GlasswareItem)
    def post(self):
        """
        Create a new glassware.
        :return: Serialized glassware object.
        """
        c = GlasswareFactory.raw_to_obj(api.payload)
        GlasswareFactory.insert_obj(obj=c)

        # Invalidate Cache
        GlasswareScanCache.invalidate()

        return ObjectSerializer.serialize(c, 'dict'), 201

    @api.response(204, 'successful delete')
    def delete(self):
        """
        Delete all glassware from the database.
        :return: None
        """
        serialized_glassware = GlasswareScanCache.retrieve()
        objs = [GlasswareFactory.raw_to_obj(glassware) for glassware in serialized_glassware]
        for c in objs:
            GlasswareFactory.delete_obj(c, commit=False)

        current_session.commit()
        GlasswareScanCache.invalidate()
        return len(objs), 204


@ns.route('/<string:slug>')
@api.doc(params={'slug': 'A glassware slug.'})
class GlasswareEndpoint(Resource):

    @api.response(200, 'success')
    def get(self, slug):
        """
        Get a glassware.
        :param slug: glassware slug
        :return: Serialized glassware object
        """
        c = GlasswareFactory.produce_obj(id=slug)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, slug):
        """
        Delete a glassware from the database.
        :param slug: Slug of a glassware
        :return: None
        """
        c = GlasswareFactory.produce_obj(id=slug)
        GlasswareFactory.delete_obj(c)
        GlasswareScanCache.invalidate()
        return None, 204
