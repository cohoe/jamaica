import json
from barbados.models import IngredientModel
from barbados.objects import Ingredient
from barbados.constants import IngredientTypes
from flask import Blueprint
from flask_api import exceptions
from jamaica.api.v1 import URL_PREFIX

app = Blueprint('ingredients', __name__, url_prefix=URL_PREFIX)
from barbados.objects import AppConfig
from barbados.connectors import PostgresqlConnector, RedisConnector

redis = RedisConnector()
sess = PostgresqlConnector(database='amari', username='postgres', password='s3krAt').Session()


@app.route('/ingredients/searchindex')
def _list():
    try:
        ingredient_name_list = redis.get(AppConfig.get('/jamaica/api/v1/ingredient_name_list_key'))
        return json.loads(ingredient_name_list)

    except KeyError:
        raise exceptions.APIException('Cache empty or other Redis error.')
    except Exception as e:
        raise exceptions.APIException(str(e))


@app.route('/ingredients/tree')
def get_ingredients():
    tree = {}

    # Categories
    categories = sess.query(IngredientModel).filter(IngredientModel.type == IngredientTypes.CATEGORY.value)
    for category in categories:
        c = Ingredient(category.slug, category.display_name, category.type, category.parent)
        if c.slug in tree.keys():
            raise Exception("Duplicate top-level slug %s" % c.slug)
        tree[c.slug] = _create_tree_entry(c)

    # Families
    family_cache = {} # key=family, value=parent(category)
    families = sess.query(IngredientModel).filter(IngredientModel.type == IngredientTypes.FAMILY.value)
    for family in families:
        f = Ingredient(family.slug, family.display_name, family.type, family.parent)
        if f.slug in tree[f.parent]['children'].keys():
            raise Exception("Duplicate family (%s) under %s" % (f.slug, f.parent))
        tree[f.parent]['children'][f.slug] = _create_tree_entry(f)
        family_cache[f.slug] = f.parent

    # Ingredients
    # There are no category-child ingredients. Need two passes to catch everyone
    sub_ingredients = []
    top_ingredient_cache = {} # key=top_ingredient, value=parent(family)
    ingredients = sess.query(IngredientModel).filter(IngredientModel.type == IngredientTypes.INGREDIENT.value)
    for ingredient in ingredients:
        # i = Ingredient(ingredient.slug, ingredient.display_name, ingredient.type, ingredient.parent)
        if ingredient.parent in family_cache.keys():
            i = Ingredient(ingredient.slug, ingredient.display_name, ingredient.type, ingredient.parent)
            tree[family_cache[i.parent]]['children'][i.parent]['children'][i.slug] = _create_tree_entry(i)
            top_ingredient_cache[i.slug] = i.parent
        else:
            sub_ingredients.append(ingredient)

    for ingredient in sub_ingredients:
        if ingredient.parent in top_ingredient_cache.keys():
            i = Ingredient(ingredient.slug, ingredient.display_name, ingredient.type, ingredient.parent)
            family = top_ingredient_cache[i.parent]
            category = family_cache[family]
            tree[category]['children'][family]['children'][i.parent]['children'][i.slug] = _create_tree_entry(i)
        else:
            print("Unable to place %s" % ingredient.slug)

    return tree


def _create_tree_entry(obj):
    return ({
        'slug': obj.slug,
        'display_name': obj.display_name,
        # 'type': obj.type_.value,
        # 'parent': obj.parent,
        'children': {}
    })