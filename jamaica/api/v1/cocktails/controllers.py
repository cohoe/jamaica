import json
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


@app.route('/cocktails/')
def get_cocktails():
    return CocktailSearch(**request.args).execute()


@app.route('/cocktail/<string:slug>')
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
