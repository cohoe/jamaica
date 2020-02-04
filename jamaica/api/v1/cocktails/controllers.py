import json
from barbados.factories import CocktailFactory
from flask import Blueprint
from flask_api import exceptions
from jamaica.api import redis, cocktail_model, AppConfig
from jamaica.api.v1 import URL_PREFIX

app = Blueprint('cocktails', __name__, url_prefix=URL_PREFIX)


@app.route('/cocktails/searchindex')
def _list():
    try:
        cocktail_name_list = redis.get(AppConfig.get('/jamaica/api/v1/cocktail_name_list_key'))
        return json.loads(cocktail_name_list)

    except KeyError:
        raise exceptions.APIException('Cache empty or other Redis error.')
    except Exception as e:
        raise exceptions.APIException(str(e))


@app.route('/cocktails/by-slug/<string:slug>')
# @cache.cached(timeout=60)
def by_slug(slug):
    try:
        result = cocktail_model.get_by_slug(slug)
        c = CocktailFactory.model_to_obj(result)
        return c.serialize()
    except KeyError:
        raise exceptions.NotFound()
    except Exception as e:
        raise exceptions.APIException(str(e))


@app.route('/cocktails/by-alpha/<string:alpha>')
def by_alpha(alpha=None):
    if not alpha or len(alpha) != 1:
        raise exceptions.ParseError('Must give a single character.')

    try:
        search_index = json.loads(redis.get(AppConfig.get('/jamaica/api/v1/cocktail_name_list_key')))
        return _get_alpha_from_cache(search_index, alpha)
    except KeyError:
        raise exceptions.APIException('Cache empty or other Redis error.')
    except Exception as e:
        raise exceptions.APIException(str(e))


def _get_alpha_from_cache(cache_index, alpha):
    if alpha == '#':
        search_results = []
        for i in range(0, 10):
            try:
                search_results += cache_index[str(i)]
            except KeyError:
                pass
    else:
        try:
            search_results = cache_index[alpha.upper()]
        except KeyError:
            search_results = []

    return search_results
