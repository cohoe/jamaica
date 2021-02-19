import os
import pytest
import json
import q

from jamaica import app

@pytest.fixture()
def client():
    with app.app.test_client() as client:
        with app.app.app_context():
            app.initialize_app(app.app)
        yield client


def test_cocktails(client):
    result = client.get('/')
    q(client.)
    assert False
    # assert len(json.loads(result.data)) > 200
