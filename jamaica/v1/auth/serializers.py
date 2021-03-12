from flask_restx import fields
from jamaica.v1.restx import api

UserItem = api.model('UserItem', {
    # 'email': fields.String(description='Users email address.', required=True),
    'username': fields.String(description='Users username', required=True),
    'password': fields.String(description='Users password.', required=True)
})
# NAH
# RedirectItem = api.model('RedirectItem', {
#     'location': fields.String(description='URL to redirect to', required=True),
#     'code': fields.String(description='HTTP redirect status code', required=True)
# })
