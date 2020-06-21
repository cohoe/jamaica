from flask_restx import fields
from jamaica.v1.restx import api
from jamaica.v1.serializers import DisplayItemBase, SearchResultBase, NullableString


IngredientSearchItem = api.inherit('IngredientSearchItem', SearchResultBase, {
    'slug': fields.String(attribute='hit.slug', description='This items slug.'),
    'display_name': fields.String(attribute='hit.display_name', description='This items display name.'),
    'kind': fields.String(attribute='hit.kind', description='The kind of this item.'),
    'parent': fields.String(attribute='hit.parent', description='The parent of this item.'),
    'aliases': fields.List(fields.String(), attribute='hit.aliases', description='Display Name aliases for this item.'),
    'elements': fields.List(fields.String(), attribute='hit.elements', description='Slug elements for this item (only if it is of kind IndexKind.'),
})

IngredientSubstitution = api.model('IngredientSubstitution', {
    'self': fields.String(attribute='self', description='The slug that you asked about.'),
    'parent': fields.String(attribute='parent', description='The parent slug of this ingredient.'),
    'parents': fields.List(fields.String, descriptiopn='List of parent slugs going to the root of the tree.'),
    'children': fields.List(fields.String(), attribute='children', description='Slugs of the children (all lower levels in the tree) of this ingredient.'),
    'siblings': fields.List(fields.String(), attribute='siblings', description='Slugs of the siblings (same level in the tree) of this ingredient.'),
})

IngredientObject = api.inherit('IngredientObject', DisplayItemBase, {
    'aliases': fields.List(fields.String(), attribute='aliases', description='Display Name aliases for this item.'),
    'elements': fields.List(fields.String(), attribute='elements', description='Slug elements for this item (only if it is of kind IndexKind.'),
    'kind': fields.String(attribute='kind', description='The kind of this item.', required=True),
    'parent': NullableString(attribute='parent', description='The parent of this item.'),  # not required for categories
})
