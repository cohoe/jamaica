import json
from jamaica import app
from barbados.models import CocktailModel
from barbados.factories import CocktailFactory
from barbados.connectors import PostgresqlConnector
# from flask import render_template


conn = PostgresqlConnector()
sess = conn.Session()


@app.route('/')
def index():
    return "Hello"


@app.route('/library/cocktails/')
def _list():
    scan_results = sess.query(CocktailModel).all()

    c_objects = []
    for result in scan_results:
        c_objects.append(CocktailFactory.model_to_obj(result).serialize())

    return json.dumps(c_objects)


@app.route('/library/cocktails/by-slug/<string:slug>')
def by_slug(slug):
    try:
        result = sess.query(CocktailModel).get(slug)
        c = CocktailFactory.model_to_obj(result)
        return json.dumps(c.serialize())
    except KeyError:
        return "not found", 404
