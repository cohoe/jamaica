from flask_restx import fields
from jamaica.v1.restx import api

CocktailSearchItem = api.model('CocktailSearchItem', {
    # 'id': fields.String(attribute='id', readOnly=True, description='ElasticSearch Document ID'),
    'score': fields.Float(attribute='score', readOnly=True, description='Search result score.'),
    'cocktail_slug': fields.String(attribute='hit.slug', description='Cocktail slug'),
    'cocktail_display_name': fields.String(attribute='hit.display_name', description='Cocktail display name'),
    'spec_slug': fields.String(attribute='hit.spec.slug', description='Spec slug'),
    'spec_display_name': fields.String(attribute='hit.spec.display_name', description='Spec display name'),
    'component_display_names': fields.List(fields.String(attribute='display_name'), attribute='hit.spec.components', description='Display names of components in this spec', example=['rum', 'sherry', 'vermouth']),
})


CocktailIndexItem = api.model('CocktailIndexItem', {
    'slug': fields.String(attribute='slug', description='Cocktail slug.', example='rum-and-coke'),
    'display_name': fields.String(attribute='display_name', description='Cocktail display name.', example='Rum & Coke'),
})

CocktailIndex = api.model('CocktailIndex', {
    # The API docs will be wrong, but this works.
    # https://github.com/python-restx/flask-restx/issues/57
    '*': fields.Wildcard(fields.List(fields.Nested(CocktailIndexItem)), description='Starting character.', example=[{'slug': 'thing', 'display_name': 'Thing'}])
})

OriginItem = api.model('OriginItem', {
    'creator': fields.String(description='Stylized name of the person who created this.', example='Sother Teague'),
    'venue': fields.String(description='Stylized name of the bar or other establishment where this object was created', example='Death & Co'),
    'location': fields.String(description='As specific place as possible where a drink was created. This may be a city or country. No formatting is enforced.', example='Boston MA'),
    'year': fields.Integer(description='The year that the drink was created. If a specific year is unknown, see "era".', example=2020),
    'era': fields.String(description='The era that the drink was created. Only to be used if year is not specific enough.', example='1840s'),
    'story': fields.String(description='A tale of the creation or evolution of this drink.', example='A long long time ago, in a galaxy far away, Naboo was under an attack.'),
})

TextItem = api.model('TextItem', {
    'text': fields.String(description='String of text.', example='The quick brown cat jumped over the energetic raccoon.')
})

CocktailImageItem = api.model('CocktailImageItem', {
    'text': fields.String(description='Description of the image. Required for ADA.', example='Boy with apple.'),
    'href': fields.String(description='URI of the image.', example='https://example.com/booze.png'),
    'credit': fields.String(description='Photographer or other image credit.', example='Michelle Jay')
})

CitationItem = api.model('CitationItem', {
    'title': fields.String(description='Title of the citation.', example='Death & Co: Modern Classic Cocktails'),
    'author': fields.List(fields.String(), description='Author of the work being cited', example=['Jillian Vose', 'Ivy Mix']),
    'date': fields.String(description='Date that the citation was published. If the exact day cannot be determined but the month can, use the first day of the month. This affects mostly old works.', example='1812-05-01'),
    'publisher': fields.String(description='Publisher of the citation.', example='Ten Speed Press'),
    'page': fields.Integer(description='If using a book or other printed medium, specify the page number.', example=69),
    'href': fields.String(description='URI of the website of the citation or to purchase the book.', example='https://example.com/booze'),
    'issue': fields.String(description='Deprecated'),
})

# SpecComponentItem = api.model('SpecComponentItem', {
#     'name': fields.String(description='Slugable name of the ingredient.', example='aged-rum'),
#     'quantity': fields.Float(description='Quantity of the ingredient in the specified unit which is described in another field. Can be omitted in certain cases such as a rinse.', example=1.5),
#     'unit': fields.String(description='Unit of measure for this component. Can be omitted in certain cases such as muddling while citrus.', example='oz'),
# })

SpecComponentItem = api.model('SpecComponentItem', {
    'slug': fields.String(description='Slug of the component.', example='aged-rum'),
    'display_name': fields.String(description='The stylized name of the component.', example='Aged Rum'),
    'quantity': fields.Float(description='Quantity of the ingredient in the specified unit which is described in another field. Can be omitted in certain cases such as a rinse.', example=1.5),
    'unit': fields.String(description='Unit of measure for this component. Can be omitted in certain cases such as muddling while citrus.', example='oz'),
    # @TODO deprecate parents?
    'parents': fields.List(fields.String(), description='List of parent slugs of this component.'),
})

# @TODO deprecate this
# GarnishItem = api.model('GarnishItem', {
#     'name': fields.String(description='Slugable name of the ingredient.', example='aged-rum'),
#     'quantity': fields.Float(description='Quantity of the ingredient in the specified unit which is described in another field. Can be omitted in certain cases such as a rinse.', example=1.5),
#     'notes': fields.List(fields.String(), description='Deprecate this, and also use proper notes expression.')
# })
GarnishItem = api.model('GarnishItem', {
    'slug': fields.String(description='Slug of the garnish.', example='lime-wedge'),
    'display_name': fields.String(description='The stylized name of the garnish.', example='Lime Wedge'),
    'quantity': fields.Float(description='Quantity of the ingredient in the specified unit which is described in another field. Can be omitted in certain cases such as a rinse.', example=1.5),
    'notes': fields.List(fields.Nested(TextItem), description='Notes on the garnish.')
})

GlasswareItem = api.model('GlasswareItem', {
    'slug': fields.String(description='Slug of the glassware.', example='old-fashioned'),
    'display_name': fields.String(description='The stylized name of the glassware.', example='Old Fashioned'),
})

ConstructionItem = api.model('ConstructionItem', {
    'slug': fields.String(description='Slug of the construction.', example='stir'),
    'display_name': fields.String(description='The stylized name of the construction.', example='Stir'),
})

ComponentCountsItem = api.model('ComponentCountsItem', {
    'all': fields.Integer(description='All components.'),
    'primary': fields.Integer(description='Primary (aka not bitters, etc).'),
    'garnish': fields.Integer(description='Garnishes'),
})

SpecItem = api.model('SpecItem', {
    'slug': fields.String(description='Identifier slug of this spec.', example='death-co'),
    'display_name': fields.String(description='The stylized name of this spec.', example='Death & Co'),
    'origin': fields.Nested(OriginItem, description='Origin of the spec.'),
    'glassware': fields.List(fields.Nested(GlasswareItem), description='Type of glass that should be used.'),
    'construction': fields.Nested(ConstructionItem, description='Construction method of the spec.'),
    'components': fields.List(fields.Nested(SpecComponentItem), description='Components of the recipe.'),
    'component_counts': fields.Nested(ComponentCountsItem, description='Count of various components'),
    'garnish': fields.List(fields.Nested(GarnishItem), description='Garnish for the recipe.'),
    'straw': fields.Boolean(description='Should a straw be used with this spec.', example=False),
    'citations': fields.List(fields.Nested(CitationItem), description='Spec citations.'),
    'images': fields.List(fields.Nested(CocktailImageItem), description='Reference images of the spec.'),
    'notes': fields.List(fields.Nested(TextItem), description='Global notes on the spec.'),
    'instructions': fields.List(fields.Nested(TextItem), description='Instructions.'),
})

# @TODO this only works on the way out, not the way in. Need to remove some fields for that.
CocktailItem = api.model('CocktailItem', {
    'slug': fields.String(description='Identifier slug of this drink.', example='la-viaa'),
    'display_name': fields.String(description='The stylized name of a drink.', example='La Viáa'),
    'status': fields.String(description='Deprecated', example='red'),
    'origin': fields.Nested(OriginItem, description='Origin of the drink (not necessarily the specific recipe).'),
    'specs': fields.List(fields.Nested(SpecItem), description='Recipes of this drink.'),
    'spec_count': fields.Integer(description='Convenience field of the number of specs associated with this drink.', example=1),
    'citations': fields.List(fields.Nested(CitationItem), description='Drink citations.'),
    'notes': fields.List(fields.Nested(TextItem), description='Global notes on the drink.'),
    'images': fields.List(fields.Nested(CocktailImageItem), description='Reference images of the drink.'),
})
