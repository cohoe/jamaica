from flask_restx import fields
from jamaica.v1.restx import api
from jamaica.v1.serializers import ComponentItem, CitationItem

InventoryItemObject = api.model('InventoryItemObject', {
    'slug': fields.String(description='Slug of this inventory item.', attribute='slug', example='regans-orange-bitters'),
    'substitutions': fields.List(fields.String(description='Slug of the substitute ingredient.', example='fee-bros-orange'),
                                 attribute='substitutes', example=['fee-bros-orange', '1821-orange'],
                                 description='List of substitute ingredient slugs.')
})

# https://flask-restx.readthedocs.io/en/latest/marshalling.html
# Even though it seems I can unify to a single line here, the guide
# tells me I shouldn't. I'll take their word for it. /shrug
InventoryItemsWildcard = fields.Wildcard(fields.Nested(InventoryItemObject), description='InventoryItemObjects')
InventoryItems = api.model('InventoryItems', {
    '*': InventoryItemsWildcard
})

InventoryObject = api.model('InventoryObject', {
    'id': fields.String(attribute='id', description='ID of this inventory.'),
    'display_name': fields.String(attribute='display_name', description='Display name of this inventory.'),
    'items': fields.Nested(InventoryItems, attribute='items'),
    'implicit_items': fields.Nested(InventoryItems, attribute='implicit_items')
})

InventoryResolutionObject = api.model('InventoryResolutionObject', {
    'slug': fields.String(attribute='slug', description='component/ingredient slug'),
    'status': fields.String(attribute='status', description='status key'),
    'substitutes': fields.List(fields.String, attribute='substitutes', description='list of substitute ingredient slugs'),
    'parents': fields.List(fields.String, attribute='parents', description='List of all parents of this ingredient.')
})

# https://flask-restx.readthedocs.io/en/latest/marshalling.html
# Even though it seems I can unify to a single line here, the guide
# tells me I shouldn't. I'll take their word for it. /shrug
count_value = fields.Wildcard(fields.Integer)
InventoryResolutionStatusCount = {'*': count_value}

InventoryResolutionSummaryObject = api.model('InventoryResolutionSummaryObject', {
    'inventory_id': fields.String(attribute='inventory_id'),
    'alpha': fields.String(attribute='alpha'),
    'cocktail_slug': fields.String(attribute='cocktail_slug'),
    'spec_slug': fields.String(attribute='spec_slug'),
    'component_count': fields.Integer(attribute='component_count'),
    'components': fields.List(fields.Nested(InventoryResolutionObject), attribute='components'),
    'construction_slug': fields.String(attribute='construction_slug'),
    'status_count': fields.Nested(InventoryResolutionStatusCount, attribute='status_count'),
    'citations': fields.List(fields.Nested(CitationItem), attribute='citations'),
    'garnish': fields.List(fields.Nested(ComponentItem), attribute='garnish'),
    'generated_at': fields.String(attribute='generated_at')
})
