from flask_restx import fields
from jamaica.v1.restx import api


IngredientSearchItem = api.model('IngredientSearchItem', {
    # 'id': fields.String(attribute='id', readOnly=True, description='ElasticSearch Document ID'),
    'score': fields.Float(attribute='score', readOnly=True, description='Search result score.'),
    'slug': fields.String(attribute='hit.slug', description='This items slug.'),
    'display_name': fields.String(attribute='hit.display_name', description='This items display name.'),
    'kind': fields.String(attribute='hit.kind', description='The kind of this item.'),
    'parent': fields.String(attribute='hit.parent', description='The parent of this item.'),
    'aliases': fields.List(fields.String(), attribute='hit.aliases', description='Display Name aliases for this item.'),
    'elements': fields.List(fields.String(), attribute='hit.elements', description='Slug elements for this item (only if it is of kind IndexKind.'),
})

IngredientIndexItem = api.model('IngredientIndexItem', {
    'slug': fields.String(attribute='slug', description='This items slug.'),
    'display_name': fields.String(attribute='display_name', description='This items display name.'),
    'aliases': fields.List(fields.String(), attribute='aliases', description='Display Name aliases for this item.'),
})

IngredientSubstitution = api.model('IngredientSubstitution', {
    'self': fields.String(attribute='self', description='The slug that you asked about.'),
    'parent': fields.String(attribute='parent', description='The parent slug of this ingredient.'),
    'parents': fields.List(fields.String, descriptiopn='List of parent slugs going to the root of the tree.'),
    'children': fields.List(fields.String(), attribute='children', description='Slugs of the children (all lower levels in the tree) of this ingredient.'),
    'siblings': fields.List(fields.String(), attribute='siblings', description='Slugs of the siblings (same level in the tree) of this ingredient.'),
})

IngredientObject = api.model('IngredientObject', {
    'slug': fields.String(attribute='slug', description='This items slug.'),
    'display_name': fields.String(attribute='display_name', description='This items display name.'),
    'aliases': fields.List(fields.String(), attribute='aliases', description='Display Name aliases for this item.'),
    'elements': fields.List(fields.String(), attribute='elements', description='Slug elements for this item (only if it is of kind IndexKind.'),
    'kind': fields.String(attribute='kind', description='The kind of this item.'),
    'parent': fields.String(attribute='parent', description='The parent of this item.'),
})


#@TODO None of this shit works.
#
# ingredient_tree_node_data = api.model('IngredientTreeNodeData', {
#     'slug': fields.String(attribute='slug', description='This items slug.'),
#     'display_name': fields.String(attribute='display_name', description='This items display name.'),
#     'aliases': fields.List(fields.String(), attribute='aliases', description='Display Name aliases for this item.'),
#     'elements': fields.List(fields.String(), attribute='hit.elements', description='Slug elements for this item (only if it is of kind IndexKind.'),
# })
#
# https://stackoverflow.com/questions/46171375/flask-restplus-recursive-json-mapping
# def recursive_tree_model(iteration=3):
#
#     field_mapping = {
#         'data': fields.Nested(ingredient_tree_node_data),
#     }
#
#     if iteration:
#         field_mapping['children'] = fields.List(fields.Nested(recursive_tree_model(iteration-1))),
#
#     return api.model("IngredientTreeNodeL%i" % iteration, field_mapping)
#
# ingredient_tree_nodewrapper2 = api.model('IngredientTreeNodeWrapper', {
#     # '*': fields.Wildcard(fields.Nested(ingredient_tree_node)),
#     '*': fields.Wildcard(fields.String)
# })
#
# ingredient_tree_node3 = api.model('IngredientTreeNode2', {
#     # '*': fields.Wildcard(fields.Nested(ingredient_tree_node_data)),
#     'data': fields.Nested(ingredient_tree_node_data),
#     # 'children': fields.List(fields.String)
#     'children': fields.List(fields.Nested(ingredient_tree_nodewrapper2))
# })
#
# ingredient_tree_node = api.model('IngredientTreeNode', {
#     # '*': fields.Wildcard(fields.Nested(ingredient_tree_node_data)),
#     'data': fields.String,
#     'children': fields.List(fields.Nested(ingredient_tree_node3))
# })
#
#
# ingredient_tree_nodewrapper = api.model('IngredientTreeNodeWrapper', {
#     # '*': fields.Wildcard(fields.Nested(ingredient_tree_node)),
#     '*': fields.Wildcard(fields.Nested(ingredient_tree_nodewrapper2))
# })
#
# ingredient_tree_node2 = api.model('IngredientTreeNode2', {
#     # '*': fields.Wildcard(fields.Nested(ingredient_tree_node_data)),
#     'data': fields.Nested(ingredient_tree_node_data),
#     # 'children': fields.List(fields.String)
#     'children': fields.List(fields.Nested(ingredient_tree_nodewrapper))
# })
#
# ingredient_tree_model = api.model('IngredientTree', {
#     'ingredients': fields.Nested(ingredient_tree_node2),
# })
#
#
