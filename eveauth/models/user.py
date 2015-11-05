import os
import uuid
import arrow
from sqlalchemy_utils import IPAddressType, ArrowType, UUIDType, PasswordType, ChoiceType
from flask.ext.restful import fields
from marshmallow import post_dump
from eveauth.models import db, ma, UserStatus


class User(db.Model):
    """
    User model
    """

    #: User UUID
    id = db.Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    #: User unique ID accross services
    user_id = db.Column(db.String, nullable=False, unique=True)
    #: User's email
    email = db.Column(db.String, nullable=False)
    password = db.Column(PasswordType(schemes=['bcrypt']), nullable=False)
    """
    User's password, automatically encrypt passwords and provide equality.
    Verifying password is as easy as::

        user = User()
        user.password = 'b'
        # '$5$rounds=80000$H.............'
        user.password == 'b'
        # True
    """
    #: User's status from :class:`UserStatus`
    status = db.Column(ChoiceType(UserStatus, impl=db.String()), nullable=False)
    #: User's last ip used to login
    last_ip = db.Column(IPAddressType, default=u'127.0.0.1', nullable=False)
    #: User's last login date
    last_login_on = db.Column(ArrowType, default=lambda: arrow.utcnow(), nullable=False)
    created_on = db.Column(ArrowType, default=arrow.utcnow, nullable=False)
    updated_on = db.Column(ArrowType, default=arrow.utcnow, nullable=False)
    anonymous = True
    authenticated = False

    def is_authenticated(self):
        """
        Returns whether the user is authenticated or not.

        :rtype: bool
        """
        return self.authenticated



class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        exclude = ('password',)

    @post_dump(pass_many=True)
    def add_envelope(self, data, many):
        if many:
            return {'items': data}
        return data
