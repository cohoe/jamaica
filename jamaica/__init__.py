import barbados.config
from flask_api import FlaskAPI
from flask_caching import Cache

app = FlaskAPI(__name__, instance_relative_config=True)
cache = Cache(app, config={'CACHE_TYPE': 'redis',
                           'CACHE_KEY_PREFIX': barbados.config.cache.jamaica_prefix,
                           'CACHE_REDIS_HOST': barbados.config.cache.redis_host,
                           'CACHE_REDIS_PORT': barbados.config.cache.redis_port})

from jamaica import views

app.config.from_object('config')
