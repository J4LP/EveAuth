import base64
import os
from flask import url_for
from flask.ext.testing import TestCase
from urllib.parse import urlencode
from eveauth.app import create_app
from eveauth.models import db
from eveauth.services import SSO


class TestSSO(TestCase):

    def create_app(self):
        os.environ['eveauth_ENV'] = 'test'
        app = create_app(config_object={
            'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'SERVER_NAME': '127.0.0.1:5000',
            'TESTING': True,
            'SSO': {
                'secret_key': 'foobar',
                'client_id': 'barfoo',
                'redirect_url': 'MetaView:register'
            }
        })
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_build_url(self):
        sso = SSO(app=self.app)
        url, state = sso.make_sso_url()
        redirect_url = urlencode({'redirect_uri': url_for(self.app.config['SSO']['redirect_url'], _external=True)})
        self.assertIn('state=' + state, url)
        self.assertIn('client_id=barfoo', url)
        self.assertIn(redirect_url, url)

    def test_make_authorization_header(self):
        sso = SSO(app=self.app)
        authorization = base64.b64decode(sso._make_basic_auth().split('Basic ')[1]).decode('utf-8')
        self.assertEqual(authorization, 'barfoo:foobar')

    def test_verify_server_error(self):
        pass


