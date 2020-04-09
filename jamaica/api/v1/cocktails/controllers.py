import json
import logging
from barbados.factories import CocktailFactory
from barbados.models import CocktailModel
from flask import Blueprint, request
from flask_api import exceptions
from barbados.objects.caches import CocktailNameCache
from jamaica.api.v1 import URL_PREFIX
from barbados.serializers import ObjectSerializer
from barbados.indexes import RecipeIndex

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
    raw_components = request.args.get(key='components', default='')
    name = request.args.get(key='name')
    components = raw_components.split(',')
    return _search(components, name)


def _search(components, name):
    logging.info("Searching on name=%s,components=%s" % (name, components))
    musts = []
    for component in components:
        # @TODO fix this
        if component == '':
            continue
        musts.append({
            'multi_match': {
                'query': component,
                'type': 'phrase_prefix',
                'fields': ['spec.components.slug', 'spec.components.display_name', 'spec.components.parents'],
            }
        })

    if name:
        musts.append({
            'multi_match': {
                'query': name,
                'type': 'phrase_prefix',
                'fields': ['spec.display_name', 'spec.slug', 'display_name', 'slug'],
            }
        })

    query_params = {
        'name_or_query': 'bool',
        'must': musts
    }

    results = RecipeIndex.search()[0:1000].query(**query_params).sort('_score').execute()
    logging.info("Got %s results." % results.hits.total.value)

    slugs = []
    for hit in results:
        logging.info("%s :: %s" % (hit.slug, hit.meta.score))
        slugs.append({
            'cocktail_slug': hit.slug,
            'cocktail_display_name': hit.display_name,
            'spec_slug': hit.spec.slug,
            'spec_display_name': hit.spec.display_name,
            'component_display_names': [component['display_name'] for component in hit.spec.components],
            'score': hit.meta.score,
        })

    return slugs


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
