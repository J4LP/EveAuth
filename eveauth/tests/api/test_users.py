import os
import arrow
from mixer._faker import faker
from flask.ext.testing import TestCase
from eveauth.app import create_app
from eveauth.models import db, User
from eveauth.tests import mixer
from link_header import parse

class TestUsersResource(TestCase):

    def create_app(self):
        os.environ['eveauth_ENV'] = 'test'
        app = create_app(config_object={
            'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'TESTING': True,
            'SSO': {
                'secret_key': 'foobar',
                'client_id': 'barfoo',
                'redirect_url': 'MetaView:register'
            }
        })
        with app.app_context():
            mixer.init_app(app)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index_empty(self):
        res = self.client.get('/api/users')
        self.assertEqual(int(res.headers['X-Total-Count']), 0)
        self.assertEqual(len(res.json['items']), 0)

    def test_index_pagination(self):
        users = mixer.cycle(50).blend(User, last_ip=faker.ipv4())
        res = self.client.get('/api/users')
        self.assertEqual(int(res.headers['X-Total-Count']), 50)
        self.assertEqual(len(res.json['items']), 20)
        next_link = parse(res.headers['Link']).links_by_attr_pairs([('rel', 'next')])[0]
        next_page = self.client.get(next_link.href)
        self.assertEqual(int(next_page.headers['X-Total-Count']), 50)
        self.assertEqual(len(next_page.json['items']), 20)
        self.assertTrue('page=2' in parse(next_page.headers['Link']).links_by_attr_pairs([('rel', 'self')])[0].href)
