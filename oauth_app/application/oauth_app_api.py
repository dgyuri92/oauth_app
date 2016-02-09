"""
    oauth_app : An extendable REST API authorization connector for OAuth2 providers
     oauth_app : Minimalistic Flask-based REST service that proxies authorized API requests to
     external HTTP services that implement the OAuth2 provider interface

    Copyright (C) Gyorgy Demarcsek, 2016
"""
from flask import request, redirect, url_for, session
import json

from . import app, CsrfToken
from .oauth2_utils import OAuth2AuthError, OAuth2ServiceFactory
from .oauth2_flask_utils import OAuth2AuthorizedFlask, Oauth2TokenGetterFlask

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
    oauth = OAuth2ServiceFactory.get_oauth(app.config['OAUTH_PROVIDERS'], oauth_service)
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
    oauth = OAuth2ServiceFactory.get_oauth(app.config['OAUTH_PROVIDERS'], oauth_service)
    # Validate the CSRF token & remove it from the database if it was successful
    token = CsrfToken.get(request.args["state"])
    if token is None:
        return json.dumps({"error": "Invalid CSRF token"}, 403)

    CsrfToken.destroy(token)

    # Get access token from provider
    @Oauth2TokenGetterFlask(oauth)
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
    oauth = OAuth2ServiceFactory.get_oauth(app.config['OAUTH_PROVIDERS'], oauth_service)

    @OAuth2AuthorizedFlask(oauth)
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
    oauth = OAuth2ServiceFactory.get_oauth(app.config['OAUTH_PROVIDERS'], oauth_service)

    @OAuth2AuthorizedFlask(oauth)
    def _internal(oauth, oauth_session=None):
        # Try to ask the remote service to revoke the access token (best effort)
        try:
            oauth_session.post("/oauth/revoke")
        except ValueError:
            pass
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


@app.errorhandler(OAuth2AuthError)
def auth_error_handler(error):
    return json.dumps({"oauth2_auth_error": repr(error)}), 403
