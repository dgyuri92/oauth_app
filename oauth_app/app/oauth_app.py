"""
    oauth_app : An extendable REST API authorization connector for OAuth2 providers
     oauth_app : Minimalistic Flask-based REST service that proxies authorized API requests to
     external HTTP services that implement the OAuth2 provider interface

    Copyright (C) Gyorgy Demarcsek, 2016
"""

import json
import base64
import os

from flask import Flask, flash, request, redirect, render_template, url_for, session, sessions
from oauth2_utils import oauth2_authorized, oauth2_auth_error, oauth2_service_factory
from contextlib import contextmanager
from aes_crypto import AESCipher
from flask_kvsession import KVSessionExtension
from simplekv.fs import FilesystemStore
from threading import Lock

# Flask setup
app = Flask(__name__)
#app.session_interface = sessions.SecureCookieSessionInterface
import default_config

# Load custom configuration
app.config.from_object(default_config)
app.config.from_pyfile("app.cfg", silent=True)

# Database setup
from model import db
db.init_app(app)

# Session setup
try:
    os.makedirs(app.config['DEFAULT_SESSION_DIRECTORY'])
except FileExistsError:
    pass

# Using signed cookies here on the client side (itsdangerous)
KVSessionExtension(FilesystemStore(app.config['DEFAULT_SESSION_DIRECTORY']), app)

class oauth2_authorized_flask(oauth2_authorized):
    """
    A Flask-compatible implementation of the oauth_authorized decorator
    """
    def __init__(self, oauth_service, **kwargs):
        global request
        super().__init__(oauth_service, **kwargs)
        self._request = request

    def get_redirect_url(self):
        return url_for(self._request.endpoint, oauth_service=self._oauth_service.name, _external=True)

    def get_request_params(self):
        return self._request.args

    def handle_unatuhorized(self):
        return redirect(url_for('login', oauth_service=self._oauth_service.name))

@app.route('/')
def index():
    return json.dumps({"status": "ready"})


@app.route('/<oauth_service>/login')
def login(oauth_service):
    oauth = oauth2_service_factory.get_oauth(app.config['OAUTH_PROVIDERS'], oauth_service)
    redirect_uri = url_for('authorize_callback',
                            oauth_service=oauth_service,
                            _external=True)
    params = {'redirect_uri': redirect_uri, 'scope': oauth.scope, 'response_type': 'code'}
    # Redirect to request authorization code from provider
    return redirect(oauth.get_authorize_url(**params))


@app.route('/<oauth_service>/authorize_callback')
def authorize_callback(oauth_service):
    oauth = oauth2_service_factory.get_oauth(app.config['OAUTH_PROVIDERS'], oauth_service)
    # Get access token from provider
    @oauth2_authorized_flask(oauth)
    def internal(oauth, oauth_session=None):
        user = oauth.get_identity(oauth_session)
        session["oauth_session_token"] = AESCipher(app.config['SECRET_KEY']).encrypt(oauth_session.access_token)
        return json.dumps({"authorized": True, "name": user.username,
                            "external_uid": user.service_uid,
                            "external_user_profile": me})

    return internal(oauth)

@app.route('/<oauth_service>/resource/<path:resource_path>')
def resource(oauth_service, resource_path):
    oauth = oauth2_service_factory.get_oauth(app.config['OAUTH_PROVIDERS'], oauth_service)
    print(resource_path)
    if "oauth_session_token" in session:
        encrypted_token = session["oauth_session_token"]
        access_token = AESCipher(app.config['SECRET_KEY']).decrypt(encrypted_token)
        oauth_session = oauth.get_session(access_token)
        # Use the access token to access resource from remote service
        method = getattr(oauth_session, request.method.lower())
        result = method(resource_path).json()
        return json.dumps({"resource": resource_path, "data": result})
    else:
        return redirect(url_for('login', oauth_service=oauth_service))


@app.route('/<oauth_service>/logout')
def logout(oauth_service):
    oauth = oauth2_service_factory.get_oauth(app.config['OAUTH_PROVIDERS'], oauth_service)
    if "oauth_session_token" in session:
        encrypted_token = session["oauth_session_token"]
        access_token = AESCipher(app.config['SECRET_KEY']).decrypt(encrypted_token)
        oauth_session = oauth.get_session(access_token)
        oauth_session.close()

    session.clear()
    return json.dumps({"logged_out": True})


@app.errorhandler(oauth2_auth_error)
def auth_error(e):
    return json.dumps({"oauth2_auth_error": repr(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        db.session.commit()
    if app.config['DEBUG']:
        from werkzeug.debug import DebuggedApplication
        app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
    app.run(host='0.0.0.0', port=80, debug=app.config['DEBUG'])
