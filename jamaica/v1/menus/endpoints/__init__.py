import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.menus.serializers import MenuObject, MenuSearchItem
from jamaica.v1.menus.parsers import menu_list_parser
from flask_sqlalchemy_session import current_session

from barbados.factories import MenuFactory
from barbados.serializers import ObjectSerializer
from barbados.caches import MenuScanCache
from barbados.indexers.menuindexer import MenuIndexer
from barbados.search.menu import MenuSearch

ns = api.namespace('v1/menus', description='Drink lists.')


@ns.route('/')
class MenusEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(MenuObject)
    def get(self):
        """
        List all Menus
        :return: List of Menu dicts
        """
        serialized_objects = json.loads(MenuScanCache.retrieve())
        return serialized_objects

    @api.response(200, 'success')
    @api.expect(MenuObject, validate=True)
    @api.marshal_with(MenuObject)
    def post(self):
        """
        Create a new Menu.
        :return: Menu you created.
        """
        m = MenuFactory.raw_to_obj(api.payload)
        MenuFactory.store_obj(session=current_session, obj=m)
        MenuIndexer.index(m)

        # Invalidate Cache
        MenuScanCache.invalidate()

        return ObjectSerializer.serialize(m, 'dict')

    @api.response(204, 'successful delete')
    def delete(self):
        """
        Delete all menus from the database. There be dragons here.
        :return: Number of items deleted.
        """
        objects = MenuFactory.produce_all_objs(session=current_session)
        for m in objects:
            MenuFactory.delete_obj(session=current_session, obj=m, commit=False)

        MenuIndexer.empty()
        current_session.commit()
        MenuScanCache.invalidate()

        return len(objects)


@ns.route('/search')
class MenuSearchEndpoint(Resource):

    @api.response(200, 'success')
    @api.expect(menu_list_parser, validate=True)
    @api.marshal_list_with(MenuSearchItem)
    def get(self):
        """
        Lookup ingredients in search.
        :return: List of search result Dicts
        """
        args = menu_list_parser.parse_args(strict=True)
        return MenuSearch(**args).execute()


@ns.route('/<string:slug>')
@api.doc(params={'slug': 'A menu slug.'})
class MenuEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(MenuObject)
    def get(self, slug):
        """
        Get a single menu from the database.
        :param slug:
        :return: Serialized Menu
        """
        c = MenuFactory.produce_obj(session=current_session, id=slug)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, slug):
        """
        Delete a single menu from the database.
        :param slug:
        :return:
        """
        m = MenuFactory.produce_obj(session=current_session, id=slug)
        MenuFactory.delete_obj(session=current_session, obj=m)

        # Invalidate Cache and de-index.
        MenuScanCache.invalidate()
        MenuIndexer.delete(m)
