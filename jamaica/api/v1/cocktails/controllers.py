import json
import logging
from barbados.factories import CocktailFactory
from barbados.models import CocktailModel
from flask import Blueprint, request
from flask_api import exceptions
from barbados.objects.caches import CocktailNameCache
from jamaica.api.v1 import URL_PREFIX
from barbados.serializers import ObjectSerializer
from barbados.search.cocktail import CocktailSearch

app = Blueprint('cocktails', __name__, url_prefix=URL_PREFIX)


@app.route('/cocktails/searchindex')
def _list():
    try:
        cocktail_name_list = CocktailNameCache.retrieve()
        return json.loads(cocktail_name_list)

    except KeyError:
        raise exceptions.APIException('Cache empty or other Redis error.')
    except Exception as e:
        raise exceptions.APIException(str(e))


@app.route('/cocktails/by-slug/<string:slug>')
# @cache.cached(timeout=60)
def by_slug(slug):
    try:
        result = CocktailModel.get_by_slug(slug)
        c = CocktailFactory.model_to_obj(result)
        return ObjectSerializer.serialize(c, 'dict')
    except KeyError:
        raise exceptions.NotFound()
    except Exception as e:
        raise exceptions.APIException(str(e))


@app.route('/cocktails/by-alpha/<string:alpha>')
def by_alpha(alpha=None):
    if not alpha or len(alpha) != 1:
        raise exceptions.ParseError('Must give a single character.')

    try:
        search_index = json.loads(CocktailNameCache.retrieve())
        return _get_alpha_from_cache(search_index, alpha)
    except KeyError:
        raise exceptions.APIException('Cache empty or other Redis error.')
    except Exception as e:
        raise exceptions.APIException(str(e))


@app.route('/cocktails/')
def get_cocktails():
    return CocktailSearch(**request.args).execute()


def _get_alpha_from_cache(cache_index, alpha):
    """
    '#' is '%23' in HTML, and really means both # and 0-9 in our
    world. Since this operates on slugs we don't need to actually
    search on literal '#' at this time.
    :param cache_index: Name index dictionary.
    :param alpha: First character of search term.
    :return: List of results.
    """
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
