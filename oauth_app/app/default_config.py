SQLALCHEMY_DATABASE_URI = 'sqlite:///oauth_app_data.db'
SECRET_KEY = '\xfb\x12\xdf\xa1@idgyjr92\xd6>V\xc0msc\xbb\x8fp\x16#Z\x0b\x81\xeb\x16\xab$_\x11bmevik'

OAUTH_PROVIDERS={
    "gitlab": {
        "OAUTH_CLIENT_ID": '06f264f0937bb230b40539a3bb7cc9cb5c839d7f6ff8d161688bd14b1baaaa62',
        "OAUTH_CLIENT_SECRET": '215a1adbdef787b3abbbbdf4c5566db750086bb442f32223c5d43c0963bec51b',
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
