SQLALCHEMY_DATABASE_URI = 'sqlite:///www-data/oauth_app_data.db'
SECRET_KEY = '\xfb\x12\xdf\xa1@idgyjr92\xd6>V\xc0msc\xbb\x8fp\x16#Z\x0b\x81\xeb\x16\xab$_\x11bmevik'

OAUTH_PROVIDERS={
    "gitlab": {
        "OAUTH_CLIENT_ID": '183957292f7b0d66565d619180d2e415b78e637e9ceed65c3d4e59a7896b057f',
        "OAUTH_CLIENT_SECRET": '37c00831494c6ec77ac077cc05fae4eec0a8a417456ef55a10a41dda0d8eb867',
        "SERVICE_BASE_URL": 'https://gitlab',
        "ACCESS_SCOPE": "api",
        "IDENTITY_RESOURCE": "api/v3/user",
        "IDENTITY_USER_NAME_FIELD": "username",
        "IDENTITY_USER_ID_FIELD": "id"
    }
}

DEBUG = True

from datetime import timedelta
SESSION_COOKIE_SECURE = DEBUG
SESSION_TYPE = "filesystem"
PERMANENT_SESSION_LIFETIME = timedelta(seconds=3600)
SESSION_USE_SIGNER = True
DEFAULT_SESSION_DIRECTORY = "/tmp/.session"
SQLALCHEMY_TRACK_MODIFICATIONS = False
