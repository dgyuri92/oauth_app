from datetime import timedelta

SQLALCHEMY_DATABASE_URI = 'sqlite:////www-data/oauth_app_data.db'

# This must be kept secret
SECRET_KEY = '\xfb\x12\xdf\xa1@idgyjr92\xd6>V\xc0msc\xbb\x8fp\x16#Z\x0b\x81\xeb\x16\xab$_\x11bmevik'

OAUTH_PROVIDERS = {
    "gitlab": {
        "OAUTH_CLIENT_ID": '27b2c07f669fdf729d50b64742ee1a4d8dfec7603c0622f025394999b5bd8417',
        "OAUTH_CLIENT_SECRET": '11baa15494833595f403f92094a9c0e75f1ad79af72c22efde304d6d541c76bf',
        "SERVICE_BASE_URL": 'https://gitlab',
        "ACCESS_SCOPE": "api",
        "IDENTITY_RESOURCE": "api/v3/user",
        "IDENTITY_USER_NAME_FIELD": "username",
        "IDENTITY_USER_ID_FIELD": "id"
    }
}

DEBUG = True # For development only

SESSION_COOKIE_SECURE = not DEBUG
SESSION_TYPE = "filesystem"
# We must expire sessions
PERMANENT_SESSION_LIFETIME = SESSION_SET_TTL = timedelta(seconds=3600)
# We want to get our cookies signed, like in JWT/JWS, but for simplicity
# we prefer symmetric cryptography (e.g.: HMAC-SHA256 with itsdangerous)
SESSION_USE_SIGNER = True
DEFAULT_SESSION_DIRECTORY = "/tmp/.session"
SQLALCHEMY_TRACK_MODIFICATIONS = False
