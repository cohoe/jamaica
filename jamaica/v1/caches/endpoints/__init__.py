from flask_restx import Resource
from jamaica.v1.restx import api

from barbados.caches import Caches

ns = api.namespace('v1/caches', description='Caches.')


@ns.route('')
class CachesEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Return a list of all cache keys.
        :return: List[Dict]
        """
        keys = Caches.cache_keys()
        return keys


@ns.route('/<string:key>')
@api.doc(params={'key': 'A cache key.'})
class CacheEndpoint(Resource):

    @api.response(204, 'successful invalidation')
    def delete(self, key):
        """
        Invalidate a cache at a particular key
        :param key: The cache key to invalidate
        :return: None
        """
        cache = Caches.get_cache(key)
        cache.invalidate()

    @api.response(200, 'successful population')
    def post(self, key):
        """
        Populate a cache at a particular key
        :param key: The cache key to populate
        :return: None
        """
        cache = Caches.get_cache(key)
        cache.populate()
