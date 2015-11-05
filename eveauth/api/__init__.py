from flask.ext.restful import Api
from eveauth.api.users import UsersResource

api_manager = Api(prefix='/api')
api_manager.add_resource(UsersResource, '/users', endpoint='api.users')
