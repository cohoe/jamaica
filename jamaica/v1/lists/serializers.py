from flask_restx import fields
from jamaica.v1.restx import api
from jamaica.v1.serializers import SearchResultBase, NullableString


ListItemObject = api.model('ListItemObject', {
    'cocktail_slug': fields.String(attribute='cocktail_slug', description='Slug of the cocktail.'),
    'spec_slug': NullableString(attribute='spec_slug', description='Slug of the specific spec.'),
    'highlight': fields.Boolean(attribute='highlight', description='Boolean of whether this is highlighted or not.')
})

ListObject = api.model('ListObject', {
    'id': fields.String(attribute='id', description='ID of this list.'),
    'display_name': fields.String(attribute='display_name', description='Display name of this list.'),
    'items': fields.List(fields.Nested(ListItemObject), attribute='items'),
})

ListSearchItem = api.inherit('ListSearchItem', SearchResultBase, {
    'slug': fields.String(attribute='hit.slug', description='This items slug.'),
    'display_name': fields.String(attribute='hit.display_name', description='This items display name.'),
})
