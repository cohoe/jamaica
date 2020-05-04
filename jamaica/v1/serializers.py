from flask_restx import fields
from jamaica.v1.restx import api


DisplayItemBase = api.model('DisplayItemBase', {
    'slug': fields.String(attribute='slug', description='This items slug (id).', required=True, example='la-viaa'),
    'display_name': fields.String(attribute='display_name', description='This items display name.', example='La Viaa'),
})

SearchResultBase = api.model('SearchResultBase', {
    'score': fields.Float(attribute='score', readOnly=True, description='Search result score.'),
})

TextItem = api.model('TextItem', {
    'text': fields.String(description='String of text.', example='The quick brown cat jumped over the energetic raccoon.', required=True),
    'author': fields.String(description='Author of this text.', example='root'),
    'datetime': fields.String(description='UTC timestamp (datetime.datetime.isoformat())', example='2020-05-04T02:36:11.368253', required=False)
})
