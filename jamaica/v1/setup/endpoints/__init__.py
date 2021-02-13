import os
import requests
from flask_restx import Resource
from jamaica.v1.restx import api


from barbados.services.database import DatabaseService
from barbados.services.logging import LogService
from barbados.indexes import Indexes
from barbados.caches import Caches

ns = api.namespace('v1/setup', description='setup')


@ns.route('')
class SetupEndpoint(Resource):

    @api.response(200, 'success')
    def get(self):
        """
        Setup the program.
        """
        # Reset the database.
        DatabaseService.drop_all()
        DatabaseService.create_all()

        # Setup indexes. Each index init() will drop and re-create.
        Indexes.init()
        self._kibana_settings()

        # Clear all caches.
        Caches.init()

        # Return something so we know it worked.
        return {'message': 'ok'}

    @staticmethod
    def _kibana_settings():
        """
        I am pedantic and want dark mode enabled on the Kibana instance.
        This code serves no useful purpose within the app.
        :return:
        """
        headers = {
            'kbn-version': '7.5.0',
            'Content-Type': 'application/json'
        }
        data = '{"changes":{"theme:darkMode":true}}'

        kibana_host = os.getenv('AMARI_KIBANA_HOST', default='localhost')
        resp = requests.post("http://%s:5601/api/kibana/settings" % kibana_host, headers=headers, data=data)
        if resp.status_code == 200:
            LogService.info("Kibana set to dark mode.")
        else:
            LogService.error("Error setting dark mode: %s" % resp.text)