import arrow
from flask_wtf import Form
from wtforms import StringField, SelectField, TextAreaField, validators, ValidationError, SelectMultipleField, PasswordField
from wtforms.fields.html5 import IntegerField, DateTimeField, EmailField


class LoginForm(Form):
    email = EmailField(
        'Email',
        validators=[validators.required()],
        description={
            'placeholder': 'john_doe@example.com',
            'icon': 'fa-envelope',
        }
    )
    password = PasswordField(
        'Mot de passe',
        validators=[validators.required()],
        description={
            'placeholder': 'Password',
            'icon': 'fa-lock',
        }
    )


class RegisterForm(Form):
    email = EmailField(
        'Email',
        validators=[validators.required(), validators.email()],
        description={
            'placeholder': 'john_doe@example.com',
            'icon': 'fa-envelope'
        }
    )
    password = PasswordField(
        'Mot de passe',
        validators=[validators.required()],
        description={
            'placeholder': 'Password',
            'help': ['Minimum 8 characters, please use a different password than your Eve Account'],
            'icon': 'fa-lock',
        }
    )
    confirm_password = PasswordField(
        'Confirmer',
        validators=[validators.required(), validators.equal_to('password')],
        description={
            'placeholder': 'Confirm password',
            'icon': 'fa-lock'
        }
    )