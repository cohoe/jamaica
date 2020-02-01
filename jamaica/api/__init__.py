from barbados.objects import AppConfig
from barbados.connectors import PostgresqlConnector, RedisConnector

redis = RedisConnector()
sess = PostgresqlConnector(database='amari', username='postgres', password='s3krAt').Session()