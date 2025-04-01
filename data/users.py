import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    api_key = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    time_zone = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    time_tasks = orm.relationship("TimeTask", back_populates='user')
    short_tasks = orm.relationship("ShortTask", back_populates='user')
    common_tasks = orm.relationship("CommonTask", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "created_date": self.created_date,
            "api_key": self.api_key,
            "time_zone": self.time_zone,
        }