SQLALCHEMY_DATABASE_URI = 'sqlite:////www-data/oauth_app_data.db'

# This must be kept secret
SECRET_KEY = '\xfb\x12\xdf\xa1@idgyjr92\xd6>V\xc0msc\xbb\x8fp\x16#Z\x0b\x81\xeb\x16\xab$_\x11bmevik'

OAUTH_PROVIDERS = {
    "gitlab": {
        "OAUTH_CLIENT_ID": '736b58fcc9a44118b202421dbbce84cac5c9eec0ba632f03b58b31dd5f5587cf',
        "OAUTH_CLIENT_SECRET": '101327bb76ba70d656be908c4354fcda493b48d4555efd0ba11d4c7e7f1cabc7',
        "SERVICE_BASE_URL": 'https://gitlab',
        "ACCESS_SCOPE": "api",
        "IDENTITY_RESOURCE": "api/v3/user",
        "IDENTITY_USER_NAME_FIELD": "username",
        "IDENTITY_USER_ID_FIELD": "id"
    }
}

DEBUG = True # For development only

from datetime import timedelta
SESSION_COOKIE_SECURE = DEBUG
SESSION_TYPE = "filesystem"
# We must expire sessions
PERMANENT_SESSION_LIFETIME = SESSION_SET_TTL = timedelta(seconds=3600)
# We want to get our cookies signed, like in JWT/JWS, but for simplicity
# we prefer symmetric cryptography (e.g.: HMAC-SHA256 with itsdangerous)
SESSION_USE_SIGNER = True
DEFAULT_SESSION_DIRECTORY = "/tmp/.session"
SQLALCHEMY_TRACK_MODIFICATIONS = False
