from flask_restx import fields
from jamaica.v1.restx import api
from jamaica.v1.serializers import DisplayItemBase, SearchResultBase, ComponentItem, TextItem


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
    'kind': fields.String(attribute='kind', description='The kind of this ingredient.'),
    'parent': fields.String(attribute='parent', description='The parent slug of this ingredient.'),
    'parents': fields.List(fields.String, descriptiopn='List of parent slugs going to the root of the tree.'),
    'children': fields.List(fields.String(), attribute='children', description='Slugs of the children (all lower levels in the tree) of this ingredient.'),
    'siblings': fields.List(fields.String(), attribute='siblings', description='Slugs of the siblings (same level in the tree) of this ingredient.'),
    'implies': fields.List(fields.String(), attribute='implies', description='List of slugs that this implies'),
    'implies_root': fields.String(attribute='implies_root', description='Slug of the root family of ingredients.')
})

IngredientConditionItem = api.model('IngredientConditionItem', {
    'bin_op': fields.String(attribute='bin_op'),
    'field': fields.String(attribute='field'),
    'operator': fields.String(attribute='operator'),
    'value': fields.String(attribute='value'),
})

IngredientObject = api.inherit('IngredientObject', DisplayItemBase, {
    'aliases': fields.List(fields.String(), attribute='aliases', description='Display Name aliases for this item.'),
    'elements': fields.List(fields.String(), attribute='elements', description='Slug elements for this item (only if it is of kind IndexKind.'),
    'kind': fields.String(attribute='kind', description='The kind of this item.', required=True),
    'parent': fields.String(attribute='parent', description='The parent of this item.', required=False),  # not required for categories
    'conditions': fields.List(fields.Nested(IngredientConditionItem), attribute='conditions', description='List of query conditions that fill this index.', required=False),
    'last_refresh': fields.String(attribute='last_refresh', description='datetime of the last refresh of this object.', required=False),
    'elements_include': fields.List(fields.String(), attribute='elements_include', required=False),
    'elements_exclude': fields.List(fields.String(), attribute='elements_exclude', required=False),
    'components': fields.List(fields.Nested(ComponentItem), description='List of components to make this ingredient'),
    'instructions': fields.List(fields.Nested(TextItem), description='List of instructions to make this ingredient'),
})
