
from flask_api import FlaskAPI
from flask_caching import Cache

from jamaica.api.v1.ingredients.controllers import app as ingredients
from jamaica.api.v1.cocktails.controllers import app as cocktails
from jamaica.api.v1.cache.controllers import app as cache


app = FlaskAPI(__name__, instance_relative_config=True)
# flask_cache = Cache(app, config={'CACHE_TYPE': 'redis',
#                                  'CACHE_KEY_PREFIX': barbados.config.cache.jamaica_prefix,
#                                  'CACHE_REDIS_HOST': barbados.config.cache.redis_host,
#                                  'CACHE_REDIS_PORT': barbados.config.cache.redis_port})

app.register_blueprint(ingredients)
app.register_blueprint(cocktails)
app.register_blueprint(cache)

app.config.from_object('config')

