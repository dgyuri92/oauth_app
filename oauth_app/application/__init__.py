import os

from flask import Flask
from flask_kvsession import KVSessionExtension
from simplekv.fs import FilesystemStore

from . import default_config
from .model import db, CsrfToken

# Flask setup
app = Flask(__name__)

# Load custom configuration
app.config.from_object(default_config)
app.config.from_pyfile("app.cfg", silent=True)

# Database setup
db.init_app(app)

# Session setup
try:
    os.makedirs(app.config['DEFAULT_SESSION_DIRECTORY'])
except FileExistsError:
    pass

# Using signed cookies here on the client side (itsdangerous)
session_manager = KVSessionExtension(FilesystemStore(app.config['DEFAULT_SESSION_DIRECTORY']), app)

# Create database and make sure to clean up expired sessions
with app.app_context():
    db.create_all()
    try:
        session_manager.cleanup_sessions()
    except:
        pass
