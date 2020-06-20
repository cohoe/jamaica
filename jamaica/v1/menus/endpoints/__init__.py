import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.menus.serializers import MenuObject
from flask_sqlalchemy_session import current_session

from barbados.models import MenuModel
from barbados.factories import MenuFactory
from barbados.serializers import ObjectSerializer

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
        # @TODO table scan bad. cache good.
        results = current_session.query(MenuModel).all()

        serialized = []
        for result in results:
            m = MenuFactory.model_to_obj(result)
            serialized.append(ObjectSerializer.serialize(m, 'dict'))
        return serialized

    @api.response(200, 'success')
    @api.expect(MenuObject, validate=True)
    @api.marshal_with(MenuObject)
    def post(self):
        """
        Create a new Menu.
        :return: Menu you created.
        :raises IntegrityError:
        """
        i = MenuFactory.raw_to_obj(api.payload)
        current_session.add(MenuModel(**ObjectSerializer.serialize(i, 'dict')))
        current_session.commit()

        return ObjectSerializer.serialize(i, 'dict')


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
        :raises KeyError: not found
        """
        result = current_session.query(MenuModel).get(slug)
        c = MenuFactory.model_to_obj(result)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, slug):
        """
        Delete a single menu from the database.
        :param slug:
        :return:
        :raises KeyError:
        """
        result = current_session.query(MenuModel).get(slug)

        if not result:
            raise KeyError('Not found')

        current_session.delete(result)
        current_session.commit()
