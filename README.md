Project
========
This is a university assignment. The goal is to demonstrate secure usage of the OAuth2 protocol for API call authorization and simple SSO between two or more web services. The library components were designed to be re-usable and extendable. For demonstration, GitLab and a simple Python+Flask web service is used in 3-legged OAuth workflow where GitLab is used as AS and IP.

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


Status
=======
Experimental, beta, development, etc. :)

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
 * ...
