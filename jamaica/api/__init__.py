from barbados.services import AppConfig, Cache
from barbados.connectors import PostgresqlConnector
from barbados.models import CocktailModel, IngredientModel

sess = PostgresqlConnector(database='amari', username='postgres', password='s3krAt').Session()

cocktail_model = CocktailModel(session=sess)
ingredient_model = IngredientModel(session=sess)
