"""
    oauth_app : An extendable REST API authorization connector for OAuth2 providers
     oauth2_flask_utils : Concrete implementations of the decorators from oauth2_utils

    Copyright (C) Gyorgy Demarcsek, 2016
"""

from flask import request, url_for, session

from . import app
from .oauth2_utils import OAuth2Authorized, OAuth2TokenGetter
from .aes_crypto import AESCipher

class OAuth2AuthorizedFlask(OAuth2Authorized):
    """
    A Flask-compatible implementation of oauth2_authorized where access tokens
    are persisted in sesssion data encrypted with AES
    """
    def __init__(self, oauth_service, **kwargs):
        global request
        super().__init__(oauth_service, **kwargs)
        self._request = request

    def get_token(self):
        encrypted_token = session[self._oauth_service.name]["oauth_session_token"]
        access_token = AESCipher(app.config['SECRET_KEY']).decrypt(encrypted_token)

        return access_token


class Oauth2TokenGetterFlask(OAuth2TokenGetter):
    """
    A Flask-compatible implementation of oauth2_token_getter where access tokens
    are persisted in sesssion data encrypted with AES
    """
    def __init__(self, oauth_service, **kwargs):
        global request
        super().__init__(oauth_service, **kwargs)
        self._request = request

    def get_redirect_url(self):
        return url_for('authorize_callback', oauth_service=self._oauth_service.name, _external=True)

    def get_request_params(self):
        return self._request.args

    def save_token(self, token):
        session[self._oauth_service.name] = {}
        session[self._oauth_service.name]["oauth_session_token"] = AESCipher(app.config['SECRET_KEY']).encrypt(token)
