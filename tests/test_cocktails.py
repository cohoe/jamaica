import json
from .client import client
from barbados.factories.spec import SpecFactory


def test_list_get(client):
    """Test that cocktails have been imported"""
    result = client.get('/api/v1/cocktails')
    recipe_count = len(json.loads(result.data))
    assert 220 < recipe_count < 300


def test_single_get(client):
    """Test that a single cocktail was returned"""
    endpoint = '/api/v1/cocktails/martinez'
    result = client.get(endpoint)
    data = json.loads(result.data)
    assert data.get('slug') == 'martinez'


def test_search_get(client):
    """Test cocktail search"""
    endpoint = '/api/v1/cocktails/search?name=martinez'
    result = client.get(endpoint)
    result_count = len(json.loads(result.data))
    assert result_count > 0


def test_bibliography_get(client):
    """Test that the bibliography works"""
    result = client.get('/api/v1/cocktails/bibliography')
    data = json.loads(result.data)
    assert len(data) > 1


###
# Old Fashioned
###
def test_old_fashioned(client):
    """Test the Old Fashioned cocktail"""
    endpoint = '/api/v1/cocktails/old-fashioned'
    result = client.get(endpoint)
    data = json.loads(result.data)
    assert len(data.get('specs')) == 2

    for spec in data.get('specs'):
        s = SpecFactory.raw_to_obj(spec)

        if s.slug == 'death-co':
            assert s.display_name == 'Death & Co'
