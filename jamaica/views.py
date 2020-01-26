import json
import barbados.config
from jamaica import app, cache
from barbados.models import CocktailModel, IngredientModel
from barbados.factories import CocktailFactory
from barbados.connectors import PostgresqlConnector, RedisConnector
from flask_api import status, exceptions
from flask import request
from barbados.objects.ingredient import IngredientTypeEnum
from barbados.objects import Ingredient

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
        pretty = request.args.get('pretty')
        if pretty:
            return json.dumps(json.loads(cocktail_name_list), indent=2)

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
# @cache.cached(timeout=60)
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


@app.route('/library/ingredients/')
def get_ingredients():
    tree = {}

    # Categories
    categories = sess.query(IngredientModel).filter(IngredientModel.type == IngredientTypeEnum.CATEGORY.value)
    for category in categories:
        c = Ingredient(category.slug, category.display_name, category.type, category.parent)
        if c.slug in tree.keys():
            raise Exception("Duplicate top-level slug %s" % c.slug)
        tree[c.slug] = _create_tree_entry(c)

    # Families
    family_cache = {} # key=family, value=parent(category)
    families = sess.query(IngredientModel).filter(IngredientModel.type == IngredientTypeEnum.FAMILY.value)
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
    ingredients = sess.query(IngredientModel).filter(IngredientModel.type == IngredientTypeEnum.INGREDIENT.value)
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

    return json.dumps(tree)


def _create_tree_entry(obj):
    return ({
        'slug': obj.slug,
        'display_name': obj.display_name,
        # 'type': obj.type_.value,
        # 'parent': obj.parent,
        'children': {}
    })