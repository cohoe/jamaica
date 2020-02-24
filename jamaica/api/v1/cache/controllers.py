from flask import Blueprint
from jamaica.api.v1 import URL_PREFIX
from flask_api import exceptions
from barbados.objects.caches import Caches


cache_url_prefix = "%s/cache" % URL_PREFIX
app = Blueprint('cache', __name__, url_prefix=cache_url_prefix)


@app.route('/rebuild/<string:cache_key>')
def rebuild(cache_key):
    try:
        cache = Caches(cache_key)
        cache.populate()
    except KeyError:
        raise exceptions.APIException("No cache for key '%s'." % cache_key)

    return {}


@app.route('/invalidate/<string:cache_key>')
def invalidate(cache_key):
    try:
        cache = Caches(cache_key)
        cache.invalidate()
    except KeyError:
        raise exceptions.NotFound()

    return {}
