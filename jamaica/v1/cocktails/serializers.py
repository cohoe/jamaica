from flask_restx import fields
from jamaica.v1.restx import api

cocktail_list_result = api.model('CocktailListResult', {
    # 'id': fields.String(attribute='id', readOnly=True, description='ElasticSearch Document ID'),
    'score': fields.Float(attribute='score', readOnly=True, description='Search result score.'),
    'cocktail_slug': fields.String(attribute='hit.slug', description='Cocktail slug'),
    'cocktail_display_name': fields.String(attribute='hit.display_name', description='Cocktail display name'),
    'spec_slug': fields.String(attribute='hit.spec.slug', description='Spec slug'),
    'spec_display_name': fields.String(attribute='hit.spec.display_name', description='Spec display name'),
    'component_display_names': fields.List(fields.String(attribute='display_name'), attribute='hit.spec.components', description='Display names of components in this spec', example=['rum', 'sherry', 'vermouth']),
})
