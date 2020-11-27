from flask_restx import Resource
from jamaica.v1.restx import api

from barbados.caches import cache_factory

ns = api.namespace('v1/caches', description='Caches.')


@ns.route('/<string:key>')
@api.doc(params={'key': 'A cache key.'})
class CacheEndpoint(Resource):

    @api.response(204, 'successful invalidation')
    def delete(self, key):
        """
        Invalidate a cache at a particular key
        :param key: The cache key to invalidate
        :return: None
        :raises KeyError:
        """
        keys = cache_factory.cache_keys()

        if key not in keys:
            raise KeyError("Cache '%s' not configured" % key)

        cache = cache_factory.get_cache(key)
        cache.invalidate()
