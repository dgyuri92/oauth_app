"""
    oauth_app : An extendable REST API authorization connector for OAuth2 providers
     oauth2_utils : OAuth2 utility library that encapsulates the 3-legged OAuth2 workflow
     and implements OAuth2 provider factory for client applications

    Copyright (C) Gyorgy Demarcsek, 2016
"""

import hmac
import hashlib
import json
import time
import base64

from functools import wraps
from threading import Lock
from abc import ABCMeta, abstractmethod

from rauth.service import OAuth2Service
from application.model import User, db


class OAuth2AuthError(Exception):
    """
    Indicates OAuth2 authorization failure (expired access token, authorization code replay, etc.)
    """
    pass


class OAuth2Authorized:
    """
    Decorator for authorized API endpoints
    """
    __metaclass__ = ABCMeta

    def __init__(self, service,
                 response_decoder=None):

        self._oauth_service = service
        self._decoder = response_decoder if response_decoder else lambda bson: json.loads(bson.decode('utf-8'))

    @abstractmethod
    def get_token(self):
        """
        Must return an existing access token that can be used or raise an exception
        """
        pass

    def __call__(self, funct):
        @wraps(funct)
        def wrapped_funct(*args, **kwargs):
            try:
                access_token = self.get_token()
            except:
                raise OAuth2AuthError("Failed to load access token")

            oauth_session = None

            try:
                # Use existing access token to create authorized session
                oauth_session = self._oauth_service.get_session(access_token)
            except:
                raise OAuth2AuthError(self._decoder(self._oauth_service.access_token_response.content))

            kwargs["oauth_session"] = oauth_session

            with oauth_session:
                return funct(*args, **kwargs)

        return wrapped_funct


class OAuth2TokenGetter:
    """
    Decorator for authorization callback endpoints
    """
    __metaclass__ = ABCMeta

    def __init__(self, service,
                 grant_type='authorization_code',
                 code_param_name='code',
                 response_decoder=None):

        self._oauth_service = service
        self._grant_type, self._code_param_name = grant_type, code_param_name
        self._decoder = response_decoder if response_decoder else lambda bson: json.loads(bson.decode('utf-8'))

    @abstractmethod
    def get_request_params():
        """
        Must return the current request parameters (POST/GET args.) as a dict
        """
        pass

    @abstractmethod
    def get_redirect_url():
        """
        Must return the redirection URI of the OAuth 2.0 client
        """
        pass

    @abstractmethod
    def save_token(token):
        """
        Persists access token that can be re-loaded later on oauth2_authorized
        endpoints
        """
        pass

    def __call__(self, funct):
        @wraps(funct)
        def wrapped_funct(*args, **kwargs):
            redirect_uri = self.get_redirect_url()
            # First check if we have
            if self._code_param_name not in self.get_request_params():
                raise OAuth2AuthError("Authorization code required")

            request_object = dict(code=self.get_request_params()[self._code_param_name],
                                 redirect_uri=redirect_uri,
                                 grant_type=self._grant_type)

            oauth_session = None
            try:
                oauth_session = self._oauth_service.get_auth_session(
                    data=request_object,
                    decoder=self._decoder)

            except:
                raise OAuth2AuthError(self._decoder(self._oauth_service.access_token_response.content))

            kwargs["oauth_session"] = oauth_session
            self.save_token(oauth_session.access_token)

            with oauth_session:
                return funct(*args, **kwargs)

        return wrapped_funct

# TODO: Map each config key to property of oauth2_service - code will be
# shorter and simpler

class OAuth2Service(OAuth2Service):
    """
    Trivial extension of OAuth2Service that stores additional config.
    information. It can also use that information to generate CSRF tokens
    and retrieve user profile data
    """
    class CaseInsensitiveDict(dict):
        def __init__(self, orig_dict):
            super().__init__({k.lower(): v for k, v in orig_dict.items()})

        def __setitem__(self, key, value):
            super().__setitem__(key.lower(), value)

        def __getitem__(self, key):
            return super().__getitem__(key.lower())

    def __init__(self, cfg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = OAuth2Service.CaseInsensitiveDict(cfg)

    def generate_csrf_token(self):
        """
        Utility method for generating CSRF tokens. The token is just returned,
        not persisted by this method.
        """
        raw = str(time.time()) + self.client_id
        hashed = hmac.new(bytes(self.client_secret, 'utf-8'), bytes(raw, 'utf-8'), hashlib.sha1)
        return str(base64.b64encode(hashed.digest()), 'ascii')

    @property
    def scope(self):
        return self._config['access_scope']

    __default_identity_decoder__ = lambda response: response.json()
    __default_identity_query_method__ = "get"

    def get_identity(self, oauth_session, decoder=None):
        if decoder is None:
            decoder = OAuth2Service.__default_identity_decoder__
        method = getattr(oauth_session, OAuth2Service.__default_identity_query_method__)
        me = decoder(method(self._config['IDENTITY_RESOURCE']))
        user_obj = User.get_or_create(me[self._config['IDENTITY_USER_NAME_FIELD']],
                                      me[self._config['IDENTITY_USER_ID_FIELD']])
        return user_obj, me


class OAuth2ServiceFactory:
    """
    Simple factory class for oauth2_service objects
    """
    mutex = Lock()

    def __init__(self, config={}):
        self._providers = {}
        self._config = config

    def _get(self, provider_name):
        try:
            return self._providers[provider_name]
        except KeyError:
            cfg = self._config[provider_name]
            new_provider = self._providers[provider_name] = OAuth2Service(
                cfg,
                name=provider_name,
                authorize_url="".join([cfg['SERVICE_BASE_URL'], '/oauth/authorize']),
                access_token_url="".join([cfg['SERVICE_BASE_URL'], '/oauth/token']),
                client_id=cfg['OAUTH_CLIENT_ID'],
                client_secret=cfg['OAUTH_CLIENT_SECRET'],
                base_url=cfg['SERVICE_BASE_URL'])

            return new_provider

    _instance = None

    @staticmethod
    def get_oauth(cfg, name):
        with OAuth2ServiceFactory.mutex:
            if OAuth2ServiceFactory._instance is None:
                OAuth2ServiceFactory._instance = OAuth2ServiceFactory(cfg)
            return OAuth2ServiceFactory._instance._get(name)
