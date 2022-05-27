from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String
from flask_login import UserMixin


db = SQLAlchemy()


class User(db.Model, UserMixin):
    """ The user class is the one used in the database for the login """
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)
