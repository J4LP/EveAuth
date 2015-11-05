from collections import OrderedDict, namedtuple
import base64
import uuid
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import requests
from flask import url_for
from eveauth.utils import camel_to_snake


class InvalidSSORequestError(Exception):
    pass


class UnavailableSSOError(Exception):
    pass


SSOInfo = namedtuple('SSOInfo', ['character_id', 'character_name', 'character_owner_hash'])


class SSO(object):
    """
    Eve SSO service.

    It can generate SSO URLs, validate OAUTH tokens and make basic CREST requests.

    Register your application `here <https://developers.eveonline.com/applications>`_.

    Configuration:

    +---------------+-----------------------------------------------------------------+
    | secret_key    | (Required) The app secret key                                   |
    +---------------+-----------------------------------------------------------------+
    | client_id     | (Required) The app client id                                    |
    +---------------+-----------------------------------------------------------------+
    | redirect_url  | (Required) The flask endpoint used for redirection              |
    +---------------+-----------------------------------------------------------------+
    | authorize_url | (Optional) The auth URL for SSO (could be used to test on SISI) |
    +---------------+-----------------------------------------------------------------+
    | token_url     | (Optional) The token URL for SSO                                |
    +---------------+-----------------------------------------------------------------+

    """

    app = None
    secret_key = None
    client_id = None
    redirect_url = None
    authorize_url = 'https://login.eveonline.com/oauth/authorize'
    token_url = 'https://login.eveonline.com/oauth/token'
    verify_url = 'https://login.eveonline.com/oauth/verify'

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        if not app.config.get('SSO'):
            raise AttributeError('Missing SSO configuration !')
        if not app.config['SSO'].get('secret_key'):
            raise AttributeError('Missing SSO secret key !')
        if not app.config['SSO'].get('client_id'):
            raise AttributeError('Missing SSO client id !')
        if not app.config['SSO'].get('redirect_url'):
            raise AttributeError('Missing SSO redirect url !')
        self.secret_key = app.config['SSO'].get('secret_key')
        self.client_id = app.config['SSO'].get('client_id')
        self.redirect_url = app.config['SSO'].get('redirect_url')
        if app.config['SSO'].get('authorize_url'):
            self.authorize_url = app.config['SSO'].get('authorize_url')
        if app.config['SSO'].get('token_url'):
            self.token_url = app.config['SSO'].get('token_url')
        if app.config['SSO'].get('verify_url'):
            self.verify_url = app.config['SSO'].get('token_url')

    def _make_basic_auth(self):
        """
        Generate the Authorization header for SSO

        b64encode only takes in bytes and format will pollute the final string with b'xxx'

        :return: An Authorization header, ready to use in requests
        """
        return 'Basic {}'.format(base64.b64encode(bytearray('{}:{}'.format(self.client_id, self.secret_key), 'utf-8')).decode('utf-8'))

    def make_sso_url(self):
        """
        Returns the url to redirect the user to with a state parameter to store in session and verify

        :return: (url, state)  A tuple with the url and the state
        """
        state = uuid.uuid4().hex
        params = {
            'response_type': 'code',
            'redirect_uri': url_for(self.redirect_url, _external=True),
            'client_id': self.client_id,
            'scope': '',
            'state': state
        }
        url_parts = list(urlparse(self.authorize_url))
        url_parts[4] = urlencode(params)
        return urlunparse(url_parts), state

    def verify_code(self, code):
        """
        Verify the authorization code and retrieve an access token.

        :param code: code returned from SSO
        :return: an access token or exceptions
        """
        try:
            res = requests.post(self.token_url, data=OrderedDict({'grant_type': 'authorization_code', 'code': code}), headers={'Authorization': self._make_basic_auth(), 'User-Agent': 'EveAuth/0.0.1'})
            if res.status_code > 500:
                raise UnavailableSSOError()
            res_json = res.json()
            if 'error' in res_json:
                error = res_json['error']
                if error is 'invalid_request':
                    raise InvalidSSORequestError(res_json['error_description'])
            return res_json['access_token']
        except Exception as e:
            self.app.logger.exception(e)
            raise e

    def verify_account(self, token):
        """
        Use the token generated earlier to retrieve basic account info

        :param token: OAuth token
        :return: :class:`SSOInfo`
        """
        try:
            res = requests.get(self.verify_url, headers={'Authorization':  'Bearer {}'.format(token), 'User-Agent': 'EveAuth/0.0.1'})
            if res.status_code > 500:
                raise UnavailableSSOError()
            return SSOInfo(**{camel_to_snake(k): v for k, v in res.json().items() if k in ['CharacterID', 'CharacterName', 'CharacterOwnerHash']})
        except Exception as e:
            self.app.logger.exception(e)
            raise e
