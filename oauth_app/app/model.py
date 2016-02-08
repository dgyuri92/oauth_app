"""
    oauth_app : An extendable REST API authorization connector for OAuth2 providers
     model.User : Generic identity (User) model
     model.CsrfToken : Timestamped CSRF tokens

    Copyright (C) Gyorgy Demarcsek, 2016
"""

import time

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    service_uid = db.Column(db.String(120))

    def __init__(self, username, service_uid):
        self.username = username
        self.service_uid = service_uid

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def get_or_create(username, service_uid):
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(username, service_uid)
            db.session.add(user)
            db.session.commit()
        return user

class CsrfToken(db.Model):
    TTL_MAX = 1000
    token = db.Column(db.String(512), primary_key=True)
    timestamp = db.Column(db.Integer)

    def __init__(self, token):
        self.token = token
        self.timestamp = int(time.time())

    def __repr__(self):
        return '<Token %r>' % self.token

    @staticmethod
    def get(token):
        csrf = CsrfToken.query.filter_by(token=token).first()
        return csrf

    @staticmethod
    def create(token):
        token_object = CsrfToken(token)
        db.session.add(token_object)
        db.session.commit()
        return token

    @staticmethod
    def destroy(token):
        db.session.delete(token)
        current_time = int(time.time())
        for t in CsrfToken.query.filter(current_time - CsrfToken.timestamp >= CsrfToken.TTL_MAX):
            db.session.delete(t)
        db.session.commit()
