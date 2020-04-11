from flask_restx import fields
from jamaica.v1.restx import api


ingredient_list_result = api.model('IngredientListResult', {
    # 'id': fields.String(attribute='id', readOnly=True, description='ElasticSearch Document ID'),
    'score': fields.Float(attribute='score', readOnly=True, description='Search result score.'),
    'slug': fields.String(attribute='hit.slug', description='This items slug.'),
    'display_name': fields.String(attribute='hit.display_name', description='This items display name.'),
    'kind': fields.String(attribute='hit.kind', description='The kind of this item.'),
    'parent': fields.String(attribute='hit.parent', description='The parent of this item.'),
    'aliases': fields.List(fields.String(), attribute='hit.aliases', description='Display Name aliases for this item.'),
    'elements': fields.List(fields.String(), attribute='hit.elements', description='Slug elements for this item (only if it is of kind IndexKind.'),
})

cocktail_search_index_result = api.model('CocktailSearchIndexResult', {
    'slug': fields.String(attribute='slug', description='Cocktail slug.', example='rum-and-coke'),
    'display_name': fields.String(attribute='display_name', description='Cocktail display name.', example='Rum & Coke'),
})

ingredient_search_index = api.model('IngredientSearchIndex', {
    'slug': fields.String(attribute='slug', description='This items slug.'),
    'display_name': fields.String(attribute='display_name', description='This items display name.'),
    'aliases': fields.List(fields.String(), attribute='aliases', description='Display Name aliases for this item.'),
})

ingredient_substitution = api.model('IngredientSubstitution', {
    'self': fields.String(attribute='self', description='The slug that you asked about.'),
    'parent': fields.String(attribute='parent', description='The parent slug of this ingredient.'),
    'children': fields.List(fields.String(), attribute='children', description='Slugs of the children (all lower levels in the tree) of this ingredient.'),
    'siblings': fields.List(fields.String(), attribute='siblings', description='Slugs of the siblings (same level in the tree) of this ingredient.'),
})