import json
import barbados.config
from jamaica import app
from barbados.models import CocktailModel
from barbados.factories import CocktailFactory
from barbados.connectors import PostgresqlConnector, RedisConnector
from flask_api import status, exceptions

conn = PostgresqlConnector()
sess = conn.Session()


@app.route('/')
def index():
    return "Hello"


@app.route('/library/cocktails/', methods=['GET', 'POST'])
def _list():
    try:
        redis = RedisConnector()
        cocktail_name_list = redis.get(barbados.config.cache.cocktail_name_list_key)
        return cocktail_name_list
    except KeyError:
        raise exceptions.APIException('Cache empty or other Redis error.')
    except Exception as e:
        raise exceptions.APIException(str(e))


# def _list():
#     scan_results = sess.query(CocktailModel).all()
#
#     c_objects = []
#     for result in scan_results:
#         c_objects.append(CocktailFactory.model_to_obj(result).serialize())
#
#     return json.dumps(c_objects)


@app.route('/library/cocktails/by-slug/<string:slug>')
def by_slug(slug):
    try:
        result = sess.query(CocktailModel).get(slug)
        c = CocktailFactory.model_to_obj(result)
        return c.serialize()
    except KeyError:
        raise exceptions.NotFound()
    except Exception as e:
        raise exceptions.APIException(str(e))


@app.route('/library/cocktails/by-alpha/')
@app.route('/library/cocktails/by-alpha/<string:alpha>')
def by_alpha(alpha=None):
    if not alpha or len(alpha) != 1:
        raise exceptions.ParseError('Must give a single character.')

    redis = RedisConnector()
    try:
        search_index = json.loads(redis.get(barbados.config.cache.cocktail_name_list_key))
        return _get_key_from_cache(search_index, alpha)
    except KeyError:
        raise exceptions.APIException('Cache empty or other Redis error.')
    except Exception as e:
        raise exceptions.APIException(str(e))


def _get_key_from_cache(cache, key):
    if key == '#':
        search_results = []
        for i in range(0, 10):
            try:
                search_results += cache[str(i)]
            except KeyError:
                pass
    else:
        try:
            search_results = cache[key.upper()]
        except KeyError:
            search_results = []

    return search_results
