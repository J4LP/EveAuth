import uuid
import arrow
from mixer._faker import faker
from mixer.backend.sqlalchemy import GenFactory
from sqlalchemy_utils import UUIDType, IPAddressType, PasswordType, ArrowType, EmailType, ChoiceType
from eveauth.models import User, UserStatus


def arrow_generator():
    return arrow.get(faker.date_time())

def setup_mixer():
    from mixer.backend.flask import mixer
    GenFactory.generators[UUIDType] = uuid.uuid4
    GenFactory.generators[IPAddressType] = faker.ipv4
    GenFactory.generators[PasswordType] = faker.word
    GenFactory.generators[ArrowType] = arrow_generator
    GenFactory.generators[EmailType] = faker.email_address

    User.password.property.columns[0].type.context.update(schemes=['md5_crypt'])

    mixer.register(
        User,
        user_id=faker.user_name,
        password=faker.md5,
        email=faker.email_address,
        status=UserStatus.active,
        last_ip=faker.ipv4,
        last_login_on=faker.date_time_this_month,
        created_on=faker.date_time_this_month,
        updated_on=faker.date_time_this_month,
    )
    return mixer

mixer = setup_mixer()
