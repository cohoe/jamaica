from flask_restx import fields
from jamaica.v1.restx import api


DisplayItemBase = api.model('DisplayItemBase', {
    'slug': fields.String(attribute='slug', description='This items slug (id).'),
    'display_name': fields.String(attribute='display_name', description='This items display name.'),
})

SearchResultBase = api.model('SearchResultBase', {
    'score': fields.Float(attribute='score', readOnly=True, description='Search result score.'),
})

TextItem = api.model('TextItem', {
    'text': fields.String(description='String of text.', example='The quick brown cat jumped over the energetic raccoon.')
})