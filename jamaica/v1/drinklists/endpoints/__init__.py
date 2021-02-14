import json
from flask_restx import Resource
from jamaica.v1.restx import api
from jamaica.v1.drinklists.serializers import DrinkListObject, DrinkListSearchItem
from jamaica.v1.drinklists.parsers import drinklist_list_parser
from flask_sqlalchemy_session import current_session

from barbados.factories.drinklist import DrinkListFactory
from barbados.serializers import ObjectSerializer
from barbados.caches.tablescan import DrinkListScanCache
from barbados.indexers.drinklist import DrinkListIndexer
from barbados.search.drinklist import DrinkListSearch

ns = api.namespace('v1/drinklists', description='Drink lists.')


@ns.route('')
class DrinkListsEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_list_with(DrinkListObject)
    def get(self):
        """
        List all DrinkLists
        :return: List of DrinkList dicts
        """
        serialized_objects = json.loads(DrinkListScanCache.retrieve())
        return serialized_objects

    @api.response(200, 'success')
    @api.expect(DrinkListObject, validate=True)
    @api.marshal_with(DrinkListObject)
    def post(self):
        """
        Create a new DrinkList.
        :return: DrinkList you created.
        """
        m = DrinkListFactory.raw_to_obj(api.payload)
        DrinkListFactory.store_obj(obj=m)
        DrinkListIndexer.index(m)

        # Invalidate Cache
        DrinkListScanCache.invalidate()

        return ObjectSerializer.serialize(m, 'dict')

    @api.response(204, 'successful delete')
    def delete(self):
        """
        Delete all drinklists from the database. There be dragons here.
        :return: Number of items deleted.
        """
        objects = DrinkListFactory.produce_all_objs()
        for m in objects:
            DrinkListFactory.delete_obj(obj=m, commit=False)

        DrinkListIndexer.empty()
        current_session.commit()
        DrinkListScanCache.invalidate()

        return len(objects)


@ns.route('/search')
class DrinkListSearchEndpoint(Resource):

    @api.response(200, 'success')
    @api.expect(drinklist_list_parser, validate=True)
    @api.marshal_list_with(DrinkListSearchItem)
    def get(self):
        """
        Search a drinklist.
        :return: List of search result Dicts
        """
        args = drinklist_list_parser.parse_args(strict=True)
        return DrinkListSearch(**args).execute()


@ns.route('/<uuid:id>')
@api.doc(params={'id': 'A drinklist id.'})
class DrinkListEndpoint(Resource):

    @api.response(200, 'success')
    @api.marshal_with(DrinkListObject)
    def get(self, id):
        """
        Get a single drinklist from the database.
        :param id:
        :return: Serialized DrinkList
        """
        c = DrinkListFactory.produce_obj(id=id)
        return ObjectSerializer.serialize(c, 'dict')

    @api.response(204, 'successful delete')
    def delete(self, id):
        """
        Delete a single drinklist from the database.
        :param id:
        :return:
        """
        m = DrinkListFactory.produce_obj(id=id)
        DrinkListFactory.delete_obj(obj=m)

        # Invalidate Cache and de-index.
        DrinkListScanCache.invalidate()
        DrinkListIndexer.delete(m)
