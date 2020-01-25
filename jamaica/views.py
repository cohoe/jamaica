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
    raw_ingredients = sess.query(IngredientModel).all()

    sub_ingredients = []

    for ingredient in raw_ingredients:
        i = Ingredient(slug=ingredient.slug, display_name=ingredient.display_name, parent=ingredient.parent, type=ingredient.type)
        if i.type_ is IngredientTypeEnum.CATEGORY:
            #tree.append(_create_tree_entry(i, partial=False))
            if i.slug in tree.keys():
                raise Exception("Duplicate top-level slug %s" % i.slug)
            tree[i.slug] = _create_tree_entry(i, partial=False)
        elif i.type_ is IngredientTypeEnum.FAMILY:
            try:
                tree[i.parent]['children'][i.slug] = _create_tree_entry(i, partial=False)
            except KeyError:
                print("ERROR")
        elif i.type_ is IngredientTypeEnum.INGREDIENT:
            try:
                # There are no top-level ingredients. Always under a family
                for category_key in tree.keys():
                    tree[category_key]['children'][i.parent]['children'][i.slug] = _create_tree_entry(i, partial=False)
            except KeyError:
                # print("Will parse %s later" % i.slug)
                sub_ingredients.append(i)

    print(len(sub_ingredients))
    for i in sub_ingredients:
        placed = False
        if i.type_ != IngredientTypeEnum.INGREDIENT:
            raise Exception("Somehow got a non-ingredient")
        try:
            for category_key in tree.keys():
                for family_key in tree[category_key]['children'].keys():
                    if i.parent in tree[category_key]['children'][family_key]['children'].keys():
                        tree[category_key]['children'][family_key]['children'][i.parent]['children'][i.slug] = _create_tree_entry(i, partial=False)
                        placed = True
        except KeyError:
            print("ERROR with %s" % i.slug)

        if not placed:
            print("Unable to place %s" % i.slug)

    return json.dumps(tree, indent=2)


def _create_tree_entry(obj, partial=True):
    ret = obj.serialize()
    ret['children'] = {}
    ret['partial'] = partial

    return ret