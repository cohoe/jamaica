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
@api.doc(params={'slug': 'An index name.'})
class IndexEndpoint(Resource):

    @api.response(200, 'success')
    def get(self, name):
        """
        Get a single index
        :param name: The name key of the index.
        :return: Name of the index.
        :raises KeyError: not found
        """
        try:
            index = index_factory.get_index(name)
            return str(type(index))
        except ValueError:
            raise KeyError("Index '%s' not found" % name)

    @api.response(204, 'successful delete')
    def delete(self, name):
        """
        Delete the contents of an index.
        :param name: The name key of the index.
        :return: Number of documents deleted.
        :raises KeyError:
        """
        try:
            index = index_factory.get_index(name=name)
        except ValueError:
            raise KeyError("Index '%s' not found" % name)

        counter = index.delete_all()
        return counter


@ns.route('/<string:name>/reindex')
@api.doc(params={'slug': 'An index name.'})
class IndexReindexEndpoint(Resource):

    @api.response(200, 'success')
    def post(self, name):
        """
        Re-index all cocktails.
        """
        # @TODO make this generic
        from barbados.models.cocktailmodel import CocktailModel
        from barbados.factories.cocktailfactory import CocktailFactory
        results = current_session.query(CocktailModel).all()

        for result in results:
            c = CocktailFactory.model_to_obj(result)
            indexer_factory.get_indexer(c).index(c)
