import os
import uuid
import arrow
from sqlalchemy_utils import IPAddressType, ArrowType, UUIDType, PasswordType, ChoiceType
from flask.ext.restful import fields
from marshmallow import post_dump
from eveauth.models import db, ma, UserStatus
from eveauth.services.sso import SSOInfo
from eveauth.forms import RegisterForm


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
    #: If the User has been validated through CREST
    crest_validated = db.Column(db.Boolean(), default=False)
    #: When the user has been validated through CREST
    crest_validated_on = db.Column(ArrowType, nullable=True)
    #: CREST returned character id
    crest_character_id = db.Column(db.Integer(), nullable=True)
    #: CREST returned character name
    crest_character_name = db.Column(db.String(), nullable=True)
    #: CREST returned character hash
    crest_character_hash = db.Column(db.String(), nullable=True)
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

    @classmethod
    def new_crest_guest(cls, user_info: RegisterForm, crest_info: SSOInfo):
        """
        Accept a :class:`RegisterForm` and a dict returned by CREST to build a guest user

        :param RegisterForm user_info: a :class:`RegisterForm`
        :param SSOInfo crest_info: CREST info
        :return:
        """
        return User(
            user_id=crest_info.character_name.lower().replace(' ', '_'),
            email=user_info.email.data,
            password=user_info.password.data,
            status=UserStatus.crest_guest,
            crest_validated=True,
            crest_validated_on=arrow.utcnow(),
            crest_character_id=crest_info.character_id,
            crest_character_name=crest_info.character_name,
            crest_character_hash=crest_info.character_owner_hash
        )

    @staticmethod
    def exists(user_id):
        return User.query.filter_by(user_id=user_id).first() is not None



class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        exclude = ('password',)

    @post_dump(pass_many=True)
    def add_envelope(self, data, many):
        if many:
            return {'items': data}
        return data
