from flask.ext.restful import fields

class DateTimeField(fields.Raw):
    def format(self, value):
        return value.isoformat()


class UUIDField(fields.Raw):
    def format(self, value):
        return str(value)


class IPField(fields.Raw):
    def format(self, value):
        return str(value)

class PasswordField(fields.Raw):
    def format(self, value):
        return str(value.hash)


user_fields = {
    'id': UUIDField,
    'first_name': fields.String,
    'last_name': fields.String,
    'email': fields.String,
    'password': PasswordField,
    'last_ip': IPField,
    'created_on': DateTimeField,
    'updated_on': DateTimeField,
}
