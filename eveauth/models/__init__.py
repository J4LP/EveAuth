import enum
import arrow
# from flask.ext.login import LoginManager
from flask.ext.migrate import Migrate
from flask.ext.sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
# login_manager = LoginManager()


class UserStatus(enum.Enum):
    crest_guest = 'CREST Guest'
    active = 'Active'
    inactive = 'Inactive'
    banned = 'Banned'
    veteran = 'Veteran'

from .user import User, UserSchema

@db.event.listens_for(User, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    target.updated_on = arrow.utcnow()
