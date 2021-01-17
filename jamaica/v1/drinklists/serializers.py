from flask_restx import fields
from jamaica.v1.restx import api
from jamaica.v1.serializers import DisplayItemBase, SearchResultBase, NullableString

DrinkListItemObject = api.model('DrinkListItemObject', {
    'cocktail_slug': fields.String(attribute='cocktail_slug', description='Slug of the cocktail.'),
    'spec_slug': NullableString(attribute='spec_slug', description='Slug of the specific spec.'),
})

DrinkListObject = api.model('DrinkListObject', {
    'id': fields.String(attribute='id', description='ID of this drinklist.'),
    'display_name': fields.String(attribute='display_name', description='Display name of this drinklist.'),
    'items': fields.List(fields.Nested(DrinkListItemObject), attribute='items'),
})

DrinkListSearchItem = api.inherit('DrinkListSearchItem', SearchResultBase, {
    'slug': fields.String(attribute='hit.slug', description='This items slug.'),
    'display_name': fields.String(attribute='hit.display_name', description='This items display name.'),
})
