SQLALCHEMY_DATABASE_URI = 'sqlite:////www-data/oauth_app_data.db'

# This must be kept secret
SECRET_KEY = '\xfb\x12\xdf\xa1@idgyjr92\xd6>V\xc0msc\xbb\x8fp\x16#Z\x0b\x81\xeb\x16\xab$_\x11bmevik'

OAUTH_PROVIDERS = {
    "gitlab": {
        "OAUTH_CLIENT_ID": 'c4aa7aa833af8e8e30872db48db741fd11d56e14e98fa2a33de61ca64aeb2d19',
        "OAUTH_CLIENT_SECRET": '64efe16aa1429ac3a191451931ae7abffbc0ae86b8ddc4cb5dea7b93fdc1adfb',
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
