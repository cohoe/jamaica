from flask_restx import fields
from jamaica.v1.restx import api

UserItem = api.model('UserItem', {
    'email': fields.String(description='Users email address.', required=True),
    'password': fields.String(description='Users password.', required=True)
})
