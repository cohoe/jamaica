from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.lists.serializers import ListObject, ListSearchItem, ListItemObject
from jamaica.v1.lists.parsers import list_parser
from flask_sqlalchemy_session import current_session

from barbados.factories.list import ListFactory
from barbados.factories.listitem import ListItemFactory
from barbados.serializers import ObjectSerializer
from barbados.caches.tablescan import ListScanCache
from barbados.indexers.list import ListIndexer
from barbados.search.lists import ListsSearch

ns = api.namespace('v1/lists', description='Lists.')


@ns.route('')
class ListsEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(ListObject)
    def get(self):
        """
        List all Lists
        :return: List of List dicts
        """
        serialized_objects = ListScanCache.retrieve()
        return serialized_objects

    @api.response(200, 'success')
    @api.expect(ListObject, validate=True)
    @api.marshal_with(ListObject)
    def post(self):
        """
        Create a new List.
        :return: List you created.
        """
        m = ListFactory.raw_to_obj(api.payload)
        ListFactory.insert_obj(obj=m)
        ListIndexer.index(m)

        # Invalidate Cache
        ListScanCache.invalidate()

        return ObjectSerializer.serialize(m, 'dict')

    @api.response(204, 'successful delete')
    def delete(self):
        """
        Delete all Lists from the database. There be dragons here.
        :return: Number of items deleted.
        """
        objects = ListFactory.produce_all_objs()
        for m in objects:
            ListFactory.delete_obj(obj=m, commit=False)

        ListIndexer.empty()
        current_session.commit()
        ListScanCache.invalidate()

        return len(objects)


@ns.route('/search')
class ListSearchEndpoint(Resource):

    @api.response(200, 'success')
    @api.expect(list_parser, validate=True)
    @api.marshal_list_with(ListSearchItem)
    def get(self):
        """
        Search a List.
        :return: List of search result Dicts
        """
        args = list_parser.parse_args(strict=True)
        return ListsSearch(**args).execute()


@ns.route('/<uuid:id>')
@api.doc(params={'id': 'A List id.'})
class ListEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(ListObject)
    def get(self, id):
        """
        Get a single List from the database.
        :param id:
        :return: Serialized List
        """
        c = ListFactory.produce_obj(id=id)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, id):
        """
        Delete a single List from the database.
        :param id:
        :return:
        """
        m = ListFactory.produce_obj(id=id)
        ListFactory.delete_obj(obj=m)

        # Invalidate Cache and de-index.
        ListScanCache.invalidate()
        ListIndexer.delete(m)


@ns.route('/<uuid:id>/items')
@api.doc(params={'id': 'A List id.'})
class ListItemsEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(ListItemObject)
    def get(self, id):
        """
        Get an inventories items from the database.
        :param id:
        :return: Serialized List
        """
        lst = ListFactory.produce_obj(id=id)
        return [ObjectSerializer.serialize(i, 'dict') for i in lst.items]

    @api.response(200, 'success')
    @api.expect(ListItemObject, validate=True)
    @api.marshal_with(ListItemObject)
    def post(self, id):
        """
        Add an item to a list.
        :return: Item that you created.
        """
        lst = ListFactory.produce_obj(id)
        i = ListItemFactory.raw_to_obj(api.payload)

        lst.add_item(i)
        ListFactory.update_obj(obj=lst, id_attr='id')
        ListIndexer.index(lst)

        # Invalidate Cache
        ListScanCache.invalidate()

        return ObjectSerializer.serialize(i, 'dict')


@ns.route('/<uuid:id>/items/<slug>')
@api.doc(params={'id': 'A List id.', 'slug': 'item slug'})
class ListItemsItemEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(ListItemObject)
    def get(self, id, slug):
        """
        Get an inventories item.
        :param id:
        :param slug:
        :return: Serialized List
        """
        lst = ListFactory.produce_obj(id=id)
        i = lst.get_item(slug)
        return ObjectSerializer.serialize(i, 'dict')

    @api.response(200, 'success')
    @api.expect(ListItemObject, validate=True)
    @api.marshal_with(ListItemObject)
    def post(self, id, slug):
        """
        # @TODO prevent changing slugs
        Replace an inventories item.
        :param id:
        :param slug:
        :return: Serialized List
        """
        lst = ListFactory.produce_obj(id=id)
        i = ListItemFactory.raw_to_obj(api.payload)

        lst.replace_item(i)
        ListFactory.update_obj(obj=lst, id_attr='id')
        ListIndexer.index(lst)

        # Invalidate Cache
        ListScanCache.invalidate()

        return ObjectSerializer.serialize(i, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, id, slug):
        """
        Delete an item to a list.
        :param id: List ID
        :param slug: item slug
        :return: None
        """
        lst = ListFactory.produce_obj(id)

        lst.remove_item(slug)
        ListFactory.update_obj(obj=lst, id_attr='id')
        ListIndexer.index(lst)

        # Invalidate Cache
        ListScanCache.invalidate()

        return None, 204
