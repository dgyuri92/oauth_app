"""
    oauth_app : An extendable REST API authorization connector for OAuth2 providers
     model : Generic identity (User) model

    Copyright (C) Gyorgy Demarcsek, 2016
"""

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
