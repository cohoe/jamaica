from flask_restx import fields
from jamaica.v1.restx import api
from jamaica.v1.serializers import DisplayItemBase, TextItem, SpecComponentItem, CitationItem, ConstructionItem, GlasswareItem


OriginItem = api.model('OriginItem', {
    'creator': fields.String(description='Stylized name of the person who created this.', example='Sother Teague'),
    'venue': fields.String(description='Stylized name of the bar or other establishment where this object was created', example='Death & Co'),
    'location': fields.String(description='As specific place as possible where a drink was created. This may be a city or country. No formatting is enforced.', example='Boston MA'),
    'year': fields.Integer(description='The year that the drink was created. If a specific year is unknown, see "era".', example=2020),
    'era': fields.String(description='The era that the drink was created. Only to be used if year is not specific enough.', example='1840s'),
    'story': fields.String(description='A tale of the creation or evolution of this drink.', example='A long long time ago, in a galaxy far away, Naboo was under an attack.'),
})

CocktailImageItem = api.model('CocktailImageItem', {
    'text': fields.String(description='Description of the image.', example='Boy with apple.', required=True),
    'href': fields.String(description='URI of the image.', example='https://example.com/booze.png', required=True),
    'credit': fields.String(description='Photographer or other image credit.', example='Michelle Jay', required=True)
})

SpecItem = api.inherit('SpecItem', DisplayItemBase, {
    'origin': fields.Nested(OriginItem, description='Origin of the spec.'),
    'glassware': fields.List(fields.Nested(GlasswareItem), description='Type of glass that should be used.'),
    'construction': fields.Nested(ConstructionItem, description='Construction method of the spec.'),
    'components': fields.List(fields.Nested(SpecComponentItem), description='Components of the recipe.', required=True),
    'garnish': fields.List(fields.Nested(SpecComponentItem), description='Garnish for the recipe.'),
    'straw': fields.Boolean(description='Should a straw be used with this spec.', example=False),
    'citations': fields.List(fields.Nested(CitationItem), description='Spec citations.'),
    'images': fields.List(fields.Nested(CocktailImageItem), description='Reference images of the spec.'),
    'notes': fields.List(fields.Nested(TextItem), description='Global notes on the spec.'),
    'instructions': fields.List(fields.Nested(TextItem), description='Instructions.'),
})

# I'm dropping spec_count in the input/output. Lets see if this actually becomes needed.
CocktailItem = api.inherit('CocktailItem', DisplayItemBase, {
    'origin': fields.Nested(OriginItem, description='Origin of the drink (not necessarily the specific recipe).'),
    'specs': fields.List(fields.Nested(SpecItem), description='Recipes of this drink.', required=True),
    'citations': fields.List(fields.Nested(CitationItem), description='Drink citations.'),
    'notes': fields.List(fields.Nested(TextItem), description='Global notes on the drink.'),
    'images': fields.List(fields.Nested(CocktailImageItem), description='Reference images of the drink.'),
})
