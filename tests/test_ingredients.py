import json
from .client import client


def test_list_get(client):
    """Test that ingredients have been imported"""
    result = client.get('/api/v1/ingredients')
    data = json.loads(result.data)
    assert 1000 < len(data) < 1500


def test_single_get(client):
    """Test that a single ingredient was returned"""
    endpoint = '/api/v1/ingredients/rum'
    result = client.get(endpoint)
    data = json.loads(result.data)
    assert data.get('slug') == 'rum'
    assert data.get('display_name') == 'Rum'
    assert data.get('kind') == 'family'


def test_search_get(client):
    """Test ingredient search"""
    endpoint = '/api/v1/ingredients/search?kind=custom'
    result = client.get(endpoint)
    data = json.loads(result.data)
    assert len(data) > 10


def test_substitution_get(client):
    """Test that the ingredient substitution page works"""
    result = client.get('/api/v1/ingredients/el-dorado-12-year-rum/substitution')
    data = json.loads(result.data)
    assert data.get('kind') == 'product'
    assert data.get('implies_root') == 'aged-rum'
