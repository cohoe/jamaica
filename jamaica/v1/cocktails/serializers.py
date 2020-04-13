from flask_restx import fields
from jamaica.v1.restx import api

CocktailSearchItem = api.model('CocktailSearchItem', {
    # 'id': fields.String(attribute='id', readOnly=True, description='ElasticSearch Document ID'),
    'score': fields.Float(attribute='score', readOnly=True, description='Search result score.'),
    'cocktail_slug': fields.String(attribute='hit.slug', description='Cocktail slug'),
    'cocktail_display_name': fields.String(attribute='hit.display_name', description='Cocktail display name'),
    'spec_slug': fields.String(attribute='hit.spec.slug', description='Spec slug'),
    'spec_display_name': fields.String(attribute='hit.spec.display_name', description='Spec display name'),
    'component_display_names': fields.List(fields.String(attribute='display_name'), attribute='hit.spec.components', description='Display names of components in this spec', example=['rum', 'sherry', 'vermouth']),
})


CocktailIndexItem = api.model('CocktailIndexItem', {
    'slug': fields.String(attribute='slug', description='Cocktail slug.', example='rum-and-coke'),
    'display_name': fields.String(attribute='display_name', description='Cocktail display name.', example='Rum & Coke'),
})

CocktailIndex = api.model('CocktailIndex', {
    # The API does will be wrong, but this works.
    # https://github.com/python-restx/flask-restx/issues/57
    '*': fields.Wildcard(fields.List(fields.Nested(CocktailIndexItem)), description='Starting character.', example=[{'slug': 'thing', 'display_name': 'Thing'}])
})
