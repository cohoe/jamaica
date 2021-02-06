from flask import Flask, Blueprint
from jamaica import settings
from jamaica.cache import flask_cache
from flask_cors import CORS
from flask_sqlalchemy_session import flask_scoped_session
from flask_uuid import FlaskUUID

from jamaica.v1.restx import api
from jamaica.v1.cocktails.endpoints import ns as cocktails_namespace
from jamaica.v1.ingredients.endpoints import ns as ingredients_namespace
from jamaica.v1.drinklists.endpoints import ns as drinklists_namespace
from jamaica.v1.caches.endpoints import ns as caches_namespace
from jamaica.v1.inventories.endpoints import ns as inventories_namespace
from jamaica.v1.indexes.endpoints import ns as indexes_namespace
from jamaica.v1.setup.endpoints import ns as setup_namespace

from barbados.services.database import DatabaseService

app = Flask('jamaica')

# https://github.com/wbolster/flask-uuid
FlaskUUID(app)

CORS(app, origins=['0.0.0.0:8080', '0.0.0.0:3000']) # @TODO make this come from Registry, along with other app config?

# Dependent service setup
session = flask_scoped_session(DatabaseService.connector.Session, app) # this doesn't use get_session. https://flask-sqlalchemy-session.readthedocs.io/en/v1.1/
flask_cache.init_app(app)


# https://github.com/postrational/rest_api_demo/blob/master/rest_api_demo/app.py
def configure_app(flask_app):
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP
    flask_app.config['RESTPLUS_MASK_HEADER'] = settings.RESTPLUS_MASK_HEADER
    # https://github.com/python-restx/flask-restx/issues/27
    flask_app.config["PROPAGATE_EXCEPTIONS"] = False


def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')

    api.init_app(blueprint)
    api.add_namespace(cocktails_namespace)
    api.add_namespace(ingredients_namespace)
    api.add_namespace(drinklists_namespace)
    api.add_namespace(caches_namespace)
    api.add_namespace(inventories_namespace)
    api.add_namespace(indexes_namespace)
    api.add_namespace(setup_namespace)

    flask_app.register_blueprint(blueprint)


def main():
    initialize_app(app)
    app.run(debug=settings.FLASK_DEBUG, host='0.0.0.0', port=8080)


if __name__ == "__main__":
    main()
