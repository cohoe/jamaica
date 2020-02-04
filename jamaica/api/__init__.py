from barbados.objects import AppConfig
from barbados.connectors import PostgresqlConnector, RedisConnector
from barbados.models import CocktailModel, IngredientModel

redis = RedisConnector()
sess = PostgresqlConnector(database='amari', username='postgres', password='s3krAt').Session()

cocktail_model = CocktailModel(session=sess)
ingredient_model = IngredientModel(session=sess)