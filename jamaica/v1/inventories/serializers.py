from flask_restx import fields
from jamaica.v1.restx import api


class InventoryItemObject(fields.Raw):
    """
    https://flask-restx.readthedocs.io/en/latest/marshalling.html
    https://stackoverflow.com/questions/58919366/flask-restplus-fields-nested-with-raw-dict-not-model
    """
    def format(self, value):
        return {slug: self._get_formatted(obj) for slug, obj in value.items()}

    @staticmethod
    def _get_formatted(value):
        """
        Can't use Yield here because we're not a List.
        https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do
        :param value:
        :return:
        """
        return {
            'slug': value.get('slug'),
            'implied_by': value.get('implied_by'),
        }


InventoryObject = api.model('InventoryObject', {
    'id': fields.String(attribute='id', description='ID of this inventory.'),
    'display_name': fields.String(attribute='display_name', description='Display name of this inventory.'),
    'items': fields.Wildcard(InventoryItemObject, attribute='items'),
    'implicit_items': fields.Wildcard(InventoryItemObject, attribute='implicit_items'),
})

InventoryResolutionObject = api.model('InventoryResolutionObject', {
    'slug': fields.String(attribute='slug', description='component/ingredient slug'),
    'status': fields.String(attribute='status', description='status key'),
    'substitutes': fields.List(fields.String, attribute='substitutes', description='list of substitute ingredient slugs')
})

# https://flask-restx.readthedocs.io/en/latest/marshalling.html
# Even though it seems I can unify to a single line here, the guide
# tells me I shouldn't. I'll take their word for it. /shrug
count_value = fields.Wildcard(fields.Integer)
InventoryResolutionStatusCount = {'*': count_value}

InventoryResolutionSummaryObject = api.model('InventoryResolutionSummaryObject', {
    'cocktail_slug': fields.String(attribute='cocktail_slug'),
    'spec_slug': fields.String(attribute='spec_slug'),
    'components': fields.List(fields.Nested(InventoryResolutionObject), attribute='components'),
    'status_count': fields.Nested(InventoryResolutionStatusCount, attribute='status_count')
})
