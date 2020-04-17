from barbados.connectors import PostgresqlConnector
from barbados.services import Registry

db_database = Registry.get('/database/postgres/database')
db_username = Registry.get('/database/postgres/username')
db_password = Registry.get('/database/postgres/password')

pgconn = PostgresqlConnector(database=db_database, username=db_username, password=db_password)
