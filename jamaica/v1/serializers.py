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
    'author': fields.String(description='Author of this text.', example='root', required=False),
    'datetime': fields.String(description='UTC timestamp (datetime.datetime.isoformat())', example='2020-05-04T02:36:11.368253', required=False)
})

CocktailSearchItem = api.inherit('CocktailSearchItem', SearchResultBase, {
    'cocktail_slug': fields.String(attribute='hit.slug', description='Cocktail slug'),
    'cocktail_display_name': fields.String(attribute='hit.display_name', description='Cocktail display name'),
    'spec_slug': fields.String(attribute='hit.spec.slug', description='Spec slug'),
    'spec_display_name': fields.String(attribute='hit.spec.display_name', description='Spec display name'),
    'construction_slug': fields.String(attribute='hit.spec.construction.slug', description='Construction slug'),
    'component_display_names': fields.List(fields.String(attribute='display_name'), attribute='hit.spec.components', description='Display names of components in this spec', example=['rum', 'sherry', 'vermouth']),
})

ComponentItem = api.inherit('ComponentItem', DisplayItemBase, {
    'quantity': fields.Float(description='Quantity of the ingredient in the specified unit which is described in another field. Can be omitted in certain cases such as a rinse.', example=1.5),
    'unit': fields.String(description='Unit of measure for this component. Can be omitted in certain cases such as muddling while citrus.', example='oz'),
    'notes': fields.List(fields.Nested(TextItem), description='Notes on the component.'),
    'optional': fields.Boolean(description='Optionality of this component', required=False),
    'preparation': fields.String(description='Preparation of this component if special.', required=False)
})

CitationItem = api.model('CitationItem', {
    'title': fields.String(description='Title of the citation.', example='Death & Co: Modern Classic Cocktails', required=True),
    'author': fields.List(fields.String, description='Author of the work being cited', example=['Jillian Vose', 'Ivy Mix'], required=False),
    'date': fields.Date(description='Date that the citation was published.', example='01-01-1970'),
    'year': fields.Integer(description='Year if a specific date is not available.', example=1812),
    'publisher': fields.String(description='Publisher of the citation.', example='Ten Speed Press'),
    'page': fields.Integer(description='If using a book or other printed medium, specify the page number.', example=69),
    'href': fields.String(description='URI of the website of the citation or to purchase the book.', example='https://example.com/booze'),
    'issue': fields.String(description='Deprecated'),
})

ConstructionItem = api.inherit('ConstructionItem', DisplayItemBase, {
    'default_instructions': fields.List(fields.Nested(TextItem), description='List of instruction text objects.')
})

GlasswareItem = api.inherit('GlasswareItem', DisplayItemBase, {})
