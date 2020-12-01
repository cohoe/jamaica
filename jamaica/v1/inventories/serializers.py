from flask_restx import fields
from jamaica.v1.restx import api
from jamaica.v1.serializers import DisplayItemBase

InventoryItemObject = api.inherit('InventoryItemObject', DisplayItemBase, {})

InventoryObject = api.model('InventoryObject', {
    'id': fields.String(attribute='id', description='ID of this inventory.'),
    'display_name': fields.String(attribute='display_name', description='Display name of this inventory.'),
    'items': fields.List(fields.Nested(InventoryItemObject), attribute='items'),
})
