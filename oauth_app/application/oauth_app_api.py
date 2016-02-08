"""
    oauth_app : An extendable REST API authorization connector for OAuth2 providers
     oauth_app : Minimalistic Flask-based REST service that proxies authorized API requests to
     external HTTP services that implement the OAuth2 provider interface

    Copyright (C) Gyorgy Demarcsek, 2016
"""
from flask import request, redirect, render_template, url_for, session, sessions
import json

from . import app, db, CsrfToken
from .oauth2_utils import oauth2_auth_error, oauth2_service_factory
from .oauth2_flask_utils import oauth2_authorized_flask, oauth2_token_getter_flask

@app.route('/')
def index():
    """
    List available providers
    """
    return json.dumps({"status": "ready", "providers": list(app.config['OAUTH_PROVIDERS'])})


@app.route('/<oauth_service>/login')
def login(oauth_service):
    """
    Login via provider :oauth_service by requesting authorization code.
    """
    oauth = oauth2_service_factory.get_oauth(app.config['OAUTH_PROVIDERS'], oauth_service)
    # This is where to pass us the auth. code
    redirect_uri = url_for('authorize_callback',
                           oauth_service=oauth_service,
                           _external=True)

    # We generate a secure CSRF token that we expect to get back from the
    # provier in authorize_callback
    new_csrf_token = CsrfToken.create(oauth.generate_csrf_token())

    params = {'redirect_uri': redirect_uri,
              'scope': oauth.scope,
              'response_type': 'code',
              'state': new_csrf_token}
    # Send client to request authorization code from provider
    return redirect(oauth.get_authorize_url(**params))


@app.route('/<oauth_service>/authorize_callback')
def authorize_callback(oauth_service):
    """
    Authorization callback handler - must be called by the external service
    """
    oauth = oauth2_service_factory.get_oauth(app.config['OAUTH_PROVIDERS'], oauth_service)
    # Validate the CSRF token & remove it from the database if it was successful
    token = CsrfToken.get(request.args["state"])
    if token is None:
        return json.dumps({"error": "Invalid CSRF token"}, 403)

    CsrfToken.destroy(token)

    # Get access token from provider
    @oauth2_token_getter_flask(oauth)
    def _internal(oauth, oauth_session=None):
        # Retrieve user profile
        user, profile = oauth.get_identity(oauth_session)
        return json.dumps({"authorized": True, "name": user.username,
                           "external_uid": user.service_uid,
                           "external_user_profile": profile})

    return _internal(oauth)


@app.route('/<oauth_service>/resource/<path:resource_path>')
def resource(oauth_service, resource_path):
    """
    Access resource on remote service at <base_url>/<resource_path> using
    the access token (proxy request)
    """
    oauth = oauth2_service_factory.get_oauth(app.config['OAUTH_PROVIDERS'], oauth_service)

    @oauth2_authorized_flask(oauth)
    def _internal(oauth, resource_path=None, oauth_session=None):
        # Use the access token to access resource from remote service
        # Proxy the method and the rest of the path
        method = getattr(oauth_session, request.method.lower())
        try:
            result = method(resource_path).json()
        except ValueError:
            return json.dumps({"error": "No JSON object received"})
        return json.dumps({"resource": resource_path, "data": result})

    return _internal(oauth, resource_path=resource_path)


@app.route('/<oauth_service>/logout')
def logout(oauth_service):
    """
    Drop access token for service :oauth_service
    """
    oauth = oauth2_service_factory.get_oauth(app.config['OAUTH_PROVIDERS'], oauth_service)

    @oauth2_authorized_flask(oauth)
    def _internal(oauth, oauth_session=None):
        # Make sure to close the session
        oauth_session.close()
        # Empty session data
        session[oauth.name] = {}
        return json.dumps({"logged_out": True})

    return _internal(oauth)


@app.route('/logout')
def logout_from_all():
    """
    Log out from all services
    """
    # Delete all session data and the session cookie
    session.clear()
    session.destroy()
    response = app.make_response(json.dumps({"logged_out": True}))
    response.delete_cookie(app.session_cookie_name)
    return response


@app.errorhandler(oauth2_auth_error)
def auth_error_handler(error):
    return json.dumps({"oauth2_auth_error": repr(error)}), 403
