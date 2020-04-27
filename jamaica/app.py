from jamaica.database import pgconn
from flask import Flask, Blueprint
from jamaica import settings
from jamaica.v1.restx import api
from flask_cors import CORS
from flask_sqlalchemy_session import flask_scoped_session

from jamaica.v1.cocktails.endpoints import ns as cocktails_namespace
from jamaica.v1.ingredients.endpoints import ns as ingredients_namespace

app = Flask('jamaica')
CORS(app, origins=['0.0.0.0:5000', '0.0.0.0:3000']) # @TODO make this come from Registry, along with other app config?
session = flask_scoped_session(pgconn.Session, app) # this doesn't use get_session. https://flask-sqlalchemy-session.readthedocs.io/en/v1.1/

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
    flask_app.register_blueprint(blueprint)


def main():
    initialize_app(app)
    app.run(debug=settings.FLASK_DEBUG, host='0.0.0.0')


if __name__ == "__main__":
    main()
