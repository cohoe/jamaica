import json
from barbados.objects.ingredienttree import IngredientTree
from barbados.objects.ingredientkinds import CategoryKind, FamilyKind
from barbados.factories import IngredientFactory
from barbados.models import IngredientModel
from flask import Blueprint
from flask_api import exceptions
from barbados.services import AppConfig, Cache
from jamaica.api.v1 import URL_PREFIX


app = Blueprint('ingredients', __name__, url_prefix=URL_PREFIX)


@app.route('/ingredients/searchindex')
def _list():
    try:
        ingredient_name_list = Cache.get(AppConfig.get('/jamaica/api/v1/ingredient_name_list_key'))
        return json.loads(ingredient_name_list)

    except KeyError:
        raise exceptions.APIException('Cache empty or other Redis error.')
    except Exception as e:
        raise exceptions.APIException(str(e))


@app.route('/ingredients/tree')
def tree():
    ingredient_tree = IngredientTree()
    return ingredient_tree.tree.to_json(with_data=True)


@app.route('/ingredients/categories')
def categories():
    categories = IngredientModel.get_by_kind(CategoryKind)
    return [cat.slug for cat in categories]


@app.route('/ingredients/category/<string:category>/families')
def families(category):
    families = IngredientModel.get_by_kind(FamilyKind)
    return [fam.slug for fam in families if fam.parent == category]


@app.route('/ingredient/<string:node>/tree')
def subtree(node):
    ingredient_tree = IngredientTree()
    return ingredient_tree.subtree(node).to_json(with_data=True)


@app.route('/ingredient/<string:node>/parent')
def parent(node):
    ingredient_tree = IngredientTree()
    node = ingredient_tree.parent(node)
    i = IngredientFactory.node_to_obj(node)
    return i.serialize()


@app.route('/ingredient/<string:slug>/substitutions')
def substitutions(slug):
    ingredient_tree = IngredientTree()
    try:
        return ingredient_tree.substitutions(slug)
    except KeyError:
        raise exceptions.NotFound()


@app.route('/ingredient/<string:node>')
def get_node(node):
    ingredient_tree = IngredientTree()
    try:
        # @TODO do model -> object stuffs
        node = ingredient_tree.node(node)
        ingredient = IngredientModel.query.get(node.identifier)
        return ingredient.slug
    except KeyError:
        raise exceptions.NotFound()
