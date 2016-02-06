"""
    oauth_app : An extendable REST API authorization connector for OAuth2 providers
     oauth2_utils : OAuth2 utility library that encapsulates the 3-legged OAuth2 workflow
     and implements OAuth2 provider factory for client applications

    Copyright (C) Gyorgy Demarcsek, 2016
"""

import json
from functools import wraps
from threading import Lock
from abc import ABCMeta, abstractmethod

from rauth.service import OAuth2Service
from model import User, db

class oauth2_auth_error(Exception):
    """
    Indicates OAuth2 authorization failure (expired access token, authorization code replay, etc.)
    """
    pass

class oauth2_authorized:
    """
    Simple generic wrapper that performs 3-legged OAuth2 authorization via the specified
    service provider.
    """

    __metaclass__ = ABCMeta

    def __init__(self, service,
                    grant_type='authorization_code', # ONLY!
                    code_param_name='code',
                    response_decoder=None):

        self._oauth_service = service
        self._grant_type, self._code_param_name = grant_type, code_param_name
        self._decoder = response_decoder if response_decoder else lambda bson: json.loads(bson.decode('utf-8'))

    @abstractmethod
    def get_redirect_url(self): pass

    @abstractmethod
    def get_request_params(self): pass

    @abstractmethod
    def handle_unatuhorized(self): pass

    def __call__(self, funct):
        @wraps(funct)
        def wrapped_funct(*args, **kwargs):
            if not self._code_param_name in self.get_request_params():
                return self.handle_unatuhorized()

            redirect_uri = self.get_redirect_url()
            request_object = dict(code=self.get_request_params()[self._code_param_name],
                                redirect_uri=redirect_uri,
                                grant_type=self._grant_type)

            try:
                kwargs["oauth_session"] = self._oauth_service.get_auth_session(
                    data=request_object,
                    decoder=self._decoder
                )
            except:
                raise oauth2_auth_error(self._decoder(self._oauth_service.access_token_response.content))

            return funct(*args, **kwargs)

        return wrapped_funct


class oauth2_service(OAuth2Service):
    class case_insensitive_dict(dict):
        def __init__(self, orig_dict):
            super().__init__({k.lower():v for k,v in orig_dict.items()})

        def __setitem__(self, key, value):
            super().__setitem__(key.lower(), value)

        def __getitem__(self, key):
            return super().__getitem__(key.lower())

    def __init__(self, cfg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = oauth2_service.case_insensitive_dict(cfg)

    @property
    def scope(self):
        return self._config['access_scope']

    __default_identity_decoder__ = lambda response: response.json()
    __default_identity_query_method__ = "get"
    def get_identity(self, oauth_session, decoder=None):
        if decoder is None:
            decoder = oauth2_service.__default_identity_decoder__
        method = getattr(oauth_session, oauth2_service.__default_identity_query_method__)
        me = decoder(method(self._config['IDENTITY_RESOURCE']))
        return User.get_or_create(me[self._config['IDENTITY_USER_NAME_FIELD']], me[self._config['IDENTITY_USER_ID_FIELD']])


class oauth2_service_factory:
    mutex = Lock()
    def __init__(self, config={}):
        self._providers = {}
        self._config = config

    def _get(self, provider_name):
        try:
            return self._providers[provider_name]
        except KeyError:
            cfg = self._config[provider_name]
            new_provider = self._providers[provider_name] = oauth2_service(
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
        with oauth2_service_factory.mutex:
            if oauth2_service_factory._instance is None:
                oauth2_service_factory._instance = oauth2_service_factory(cfg)
            return oauth2_service_factory._instance._get(name)
