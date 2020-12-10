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
