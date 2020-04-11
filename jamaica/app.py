import jamaica.database
from flask import Flask, Blueprint
from jamaica import settings
from jamaica.v1.restx import api

from jamaica.v1.cocktails.endpoints import ns as cocktails_namespace
from jamaica.v1.ingredients.endpoints import ns as ingredients_namespace

app = Flask('jamaica')


# https://github.com/postrational/rest_api_demo/blob/master/rest_api_demo/app.py
def configure_app(flask_app):
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP
    flask_app.config['RESTPLUS_MASK_HEADER'] = settings.RESTPLUS_MASK_HEADER


def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(cocktails_namespace)
    api.add_namespace(ingredients_namespace)
    flask_app.register_blueprint(blueprint)


def main():
    initialize_app(app)
    app.run(debug=settings.FLASK_DEBUG)


if __name__ == "__main__":
    main()