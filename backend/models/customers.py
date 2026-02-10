from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from backend import db

class Customers(UserMixin, db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(128), index=True, nullable=False)
    lastname = db.Column(db.String(128), index=True, nullable=True)
    email = db.Column(db.String(256), index=True, unique=True, nullable=False)
    company = db.Column(db.String(256), index=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    phone = db.Column(db.String(128), index=True, nullable=True)


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256))
    assigned_tickets = db.relationship('Tickets', backref='agent', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

