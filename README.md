Project
========
This is a university assignment in IT security domain. The goal is to demonstrate secure usage of the OAuth2 protocol for API call authorization and simple SSO between two or more web services. The library components were designed to be re-usable and extendable. For demonstration, GitLab and a simple Python+Flask web service is used in 3-legged OAuth workflow where GitLab is used as AS and IP.

Getting started
================
The easiest way to get started with a development configuration is to use Docker. First you need to generate the SSL certificates and build the docker images.

```bash
$ pushd pki && make gitlab.pki oauth_app.pki && popd
```
Now you have the certificates, time to build the Docker images.

To build the images and start the Docker containers, you can run:

```bash
$ docker-compose up
```

Then use your browser to access your web services inside the containers. By default, the GitLab instance will listen on port 443, the OAuth2 client will listen on port 8080, both with HTTPS of course. If you are using `docker-machine` and ran `dns_setup.sh` then you can just use `https://gitlab/` and `https://oauthapp:8080/` to get started. You will need to register the application at GitLab and update the OAuth2 client credentials in the configuration.

Usage
======
Add OAuth2 providers to omniauth_providers.cfg and rebuild the Docker image. Example:

```python
OAUTH_PROVIDERS={
    "gitlab": {
        # Client id
        "OAUTH_CLIENT_ID": 'XXXXXXX',
        # Client secret
        "OAUTH_CLIENT_SECRET": 'XXXXX',
        # Base URL of provider (authorization service URL is base url + /oauth/authorize by default for the moment)
        "SERVICE_BASE_URL": 'https://my.gitlab.com',
        # Scope for access token
        "ACCESS_SCOPE": "api",
        # Path to "identity" resource (relative to base URL)
        "IDENTITY_RESOURCE": "api/v3/user",
        # Field to use to retrieve human-readable name
        "IDENTITY_USER_NAME_FIELD": "username",
        # Field to use to retrieve unique id
        "IDENTITY_USER_ID_FIELD": "id"
    },
    ...
}
```

This configuration will result in the following endpoints:


* List providers: https://oauthapp:8080/
* Login via GitLab: https://oauthapp:8080/gitlab/login
* Redirect (callback) URI for the client: https://oauthapp:8080/gitlab/authorize_callback
* Drop current GitLab access token: https://oauthapp:8080/gitlab/logout
* Access GitLab REST resource: https://oauthapp:8080/gitlab/resource/...
* Drop all access tokens (and delete session cookie): https://oauthapp:8080/logout



Status
=======
Experimental, beta, development, etc. :)

Notes: 
 * Only 3-legged workflow is supported
 * Tested only with authorization code grant type
 * OAuth 1.0 is not supported


External docs
=============
 * https://github.com/gitlabhq/gitlabhq/tree/master/doc/api
 * http://www.apiacademy.co/common-oauth-security-mistakes-threat-mitigations/
 * http://self-issued.info/docs/draft-ietf-oauth-v2-bearer.html
 * https://labs.hybris.com/2012/06/18/trying-out-oauth2-via-curl/
 * http://doc.gitlab.com/omnibus/docker/
 * http://flask-rauth.readthedocs.org/en/latest/
 * https://jwt.io/
 * https://github.com/reddit/reddit/wiki/OAuth2-Python-Example
 * http://doc.gitlab.com/ce/integration/oauth_provider.html
 * https://www.digitalocean.com/community/tutorials/an-introduction-to-oauth-2
 * http://oauthbible.com/
 * http://www.cloudidentity.com/blog/2013/01/02/oauth-2-0-and-sign-in-4/
