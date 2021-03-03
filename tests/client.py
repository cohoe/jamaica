import pytest
from jamaica import app

# https://flask.palletsprojects.com/en/1.1.x/testing/

with app.app.app_context():
    app.initialize_endpoints(app.app)


@pytest.fixture()
def client():
    with app.app.test_client() as client:
        yield client
