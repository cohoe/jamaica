from flask_restx import Resource
from jamaica.v1.restx import api
from flask_sqlalchemy_session import current_session

from barbados.indexers import indexer_factory
from barbados.indexes import index_factory


ns = api.namespace('v1/indexes', description='Search indexes.')


@ns.route('/')
class IndexesEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        List all Indexes
        :return: List of Index keys
        """
        return list(index_factory.get_indexes().keys())


@ns.route('/<string:name>')
@api.doc(params={'name': 'An index name.'})
class IndexEndpoint(Resource):

    @api.response(200, 'success')
    def post(self, name):
        """
        Re-index all objects that are supposed to be in an index.
        """
        index = index_factory.get_index(name=name)
        indexer = indexer_factory.indexer_for(index)

        counter = indexer.reindex(current_session)
        return counter

    @api.response(204, 'successful delete')
    def delete(self, name):
        """
        Delete the contents of an index.
        :param name: The name key of the index.
        :return: Number of documents deleted.
        """
        index = index_factory.get_index(name=name)
        counter = index.delete_all()

        return counter
