import json
from barbados.serializers import ObjectSerializer
from barbados.factories import IngredientFactory
from barbados.models import IngredientModel
from flask import Blueprint, request
from flask_api import exceptions
from barbados.objects.caches import UsableIngredientCache, IngredientTreeCache
from jamaica.api.v1 import URL_PREFIX
from barbados.search.ingredient import IngredientSearch


app = Blueprint('ingredients', __name__, url_prefix=URL_PREFIX)


@app.route('/ingredients/searchindex')
def _list():
    try:
        ingredient_name_list = UsableIngredientCache.retrieve()
        return json.loads(ingredient_name_list)

    except KeyError:
        raise exceptions.APIException('Cache empty or other Redis error.')
    except Exception as e:
        raise exceptions.APIException(str(e))


@app.route('/ingredients/tree')
def tree():
    ingredient_tree = IngredientTreeCache.retrieve()
    return ingredient_tree.tree.to_json(with_data=True)


@app.route('/ingredients')
def get_all():
    return IngredientSearch(**request.args).execute()


@app.route('/ingredient/<string:slug>')
def get_ingredient(slug):
    try:
        self_model = IngredientModel.get_by_slug(slug)
        if self_model is None:
            raise exceptions.NotFound
        i = IngredientFactory.to_obj(self_model)

        return ObjectSerializer.serialize(i, 'JSON')
    except KeyError:
        raise exceptions.NotFound


@app.route('/ingredient/<string:node>/tree')
def subtree(node):
    ingredient_tree = IngredientTreeCache.retrieve()
    try:
        return ingredient_tree.subtree(node).to_json(with_data=True)
    except KeyError:
        raise exceptions.NotFound


# @TODO roll this into /ingredient/<slug>
@app.route('/ingredient/<string:slug>/parents')
def parents(slug):
    try:
        ingredient_tree = IngredientTreeCache.retrieve()
        parents = ingredient_tree.parents(slug)

        return parents
    except KeyError:
        raise exceptions.NotFound


@app.route('/ingredient/<string:slug>/substitutions')
def substitutions(slug):
    ingredient_tree = IngredientTreeCache.retrieve()
    try:
        return ingredient_tree.substitutions(slug)
    except KeyError:
        raise exceptions.NotFound
