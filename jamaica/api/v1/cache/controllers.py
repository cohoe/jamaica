import json
from flask import Blueprint
from flask_api import exceptions
from barbados.models import CocktailModel
from barbados.services import AppConfig, Cache
from jamaica.api.v1 import URL_PREFIX
from barbados.models import IngredientModel


cache_url_prefix = "%s/cache" % URL_PREFIX

app = Blueprint('cache', __name__, url_prefix=cache_url_prefix)


@app.route('/rebuild/<string:cache_key>')
def rebuild(cache_key):
    if cache_key == AppConfig.get('/jamaica/api/v1/cocktail_name_list_key'):
        _build_cocktail_cache(AppConfig.get('/jamaica/api/v1/cocktail_name_list_key'))
    elif cache_key == AppConfig.get('/jamaica/api/v1/ingredient_name_list_key'):
        _build_ingredient_cache(AppConfig.get('/jamaica/api/v1/ingredient_name_list_key'))
    else:
        raise exceptions.ParseError("Unsupported cache key '%s'" % cache_key)

    return {}


@app.route('/invalidate/<string:cache_key>')
def invalidate(cache_key):
    Cache.delete(cache_key)
    return {}


def _build_cocktail_cache(cache_key):
    # This is still returning all values, just not populating them
    scan_results = CocktailModel.get_all()

    index = {}
    for result in scan_results:
        key_alpha = result.slug[0].upper()
        key_entry = {
            'slug': result.slug,
            'display_name': result.display_name
        }
        if key_alpha not in index.keys():
            index[key_alpha] = [key_entry]
        else:
            index[key_alpha].append(key_entry)

    Cache.set(cache_key, json.dumps(index))


def _build_ingredient_cache(cache_key):
    # This is still returning all values, just not populating them
    scan_results = IngredientModel.get_usable_ingredients()

    index = []
    for result in scan_results:
        index.append({
            'slug': result.slug,
            'display_name': result.display_name,
            'aliases': result.aliases,
        })

    Cache.set(cache_key, json.dumps(index))
