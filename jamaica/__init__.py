from flask_api import FlaskAPI

app = FlaskAPI(__name__, instance_relative_config=True)

from jamaica import views

app.config.from_object('config')
