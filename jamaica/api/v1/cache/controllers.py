import json
from barbados.models import CocktailModel, IngredientModel
from barbados.constants import IngredientTypes
from flask import Blueprint
from flask_api import exceptions
from jamaica.api.v1 import URL_PREFIX
from sqlalchemy import or_

cache_url_prefix = "%s/cache" % URL_PREFIX

app = Blueprint('cache', __name__, url_prefix=cache_url_prefix)
from barbados.objects import AppConfig
from barbados.connectors import PostgresqlConnector, RedisConnector

redis = RedisConnector()
sess = PostgresqlConnector(database='amari', username='postgres', password='s3krAt').Session()


@app.route('/rebuild/<string:cache_key>')
def rebuild(cache_key):
    if cache_key == AppConfig.get('/jamaica/api/v1/cocktail_name_list_key'):
        _build_cocktail_cache(AppConfig.get('/jamaica/api/v1/cocktail_name_list_key'), sess, redis)
    elif cache_key == AppConfig.get('/jamaica/api/v1/ingredient_name_list_key'):
        _build_ingredient_cache(AppConfig.get('/jamaica/api/v1/ingredient_name_list_key'), sess, redis)
    else:
        raise exceptions.ParseError("Unsupported cache key '%s'" % cache_key)

    return {}


@app.route('/invalidate/<string:cache_key>')
def invalidate(cache_key):
    redis.delete(cache_key)
    return {}


def _build_cocktail_cache(cache_key, database_session, redis_connection):
    # This is still returning all values, just not populating them
    scan_results = database_session.query(CocktailModel).add_columns(CocktailModel.slug, CocktailModel.display_name).all()

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

    redis_connection.set(cache_key, json.dumps(index))


def _build_ingredient_cache(cache_key, database_session, redis_connection):
    # This is still returning all values, just not populating them
    scan_results = database_session.query(IngredientModel).add_columns(IngredientModel.slug, IngredientModel.display_name).filter(
        or_(IngredientModel.type == IngredientTypes.INGREDIENT.value, IngredientModel.type == IngredientTypes.FAMILY.value))

    index = []
    for result in scan_results:
        index.append({
            'slug': result.slug,
            'display_name': result.display_name
        })

    redis_connection.set(cache_key, json.dumps(index))
