from flask_restx import fields
from jamaica.v1.restx import api
from jamaica.v1.serializers import DisplayItemBase

MenuItemObject = api.model('MenuItemObject', {
    'cocktail_slug': fields.String(attribute='cocktail_slug', description='Slug of the cocktail.'),
    'spec_slug': fields.String(attribute='spec_slug', description='Slug of the specific spec.'),
})

MenuObject = api.inherit('MenuObject', DisplayItemBase, {
    'items': fields.List(fields.Nested(MenuItemObject), attribute='items'),
})
