from flask_caching import Cache as FlaskCache
from barbados.services.cache import CacheService

flask_cache = FlaskCache(config=CacheService.get_flask_config())
