from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    u_name = db.Column(db.String(20), unique=True)
    u_fname = db.Column(db.String(50))
    u_lname = db.Column(db.String(50))
    u_email = db.Column(db.String(150), unique=True)
    u_password = db.Column(db.String(150))
    u_type = db.Column(db.String(5))
    u_date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    u_last_login = db.Column(db.DateTime(timezone=True), default=func.now())
    kids = db.relationship('Child')


class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    c_first_name = db.Column(db.String(50))
    c_last_name = db.Column(db.String(50))
    c_birth_date = db.Column(db.Date())
    c_gender = db.Column(db.String(6))
    c_height = db.Column(db.Integer)
    c_weight = db.Column(db.Float(precision='3,2'))
    c_parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    history = db.relationship('History')


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer)
    child_height = db.Column(db.Integer)
    child_weight = db.Column(db.Float(precision='3,2'))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    child_id = db.Column(db.ForeignKey('child.id'))
