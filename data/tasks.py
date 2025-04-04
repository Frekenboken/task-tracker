import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

from utils import generate_random_color


class TimeTask(SqlAlchemyBase):
    __tablename__ = 'time-tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    start_time = sqlalchemy.Column(sqlalchemy.Time)
    end_time = sqlalchemy.Column(sqlalchemy.Time, nullable=True)
    duration = sqlalchemy.Column(sqlalchemy.Time, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.Date)
    done = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    color = sqlalchemy.Column(sqlalchemy.String, default=generate_random_color)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    user = orm.relationship('User')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_time": str(self.start_time) if self.start_time else None,
            "end_time": str(self.end_time) if self.end_time else None,
            "duration": str(self.duration) if self.duration else None,
            "date": str(self.date),
            "done": self.done,
            "color": self.color,
            "created_date": str(self.created_date),
        }


class ShortTask(SqlAlchemyBase):
    __tablename__ = 'short-tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.Date)
    done = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    user = orm.relationship('User')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "date": str(self.date),
            "done": self.done,
            "created_date": str(self.created_date),
        }


class CommonTask(SqlAlchemyBase):
    __tablename__ = 'common-tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    done = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    user = orm.relationship('User')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "done": self.done,
            "created_date": str(self.created_date),
        }
