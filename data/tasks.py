import datetime
from .db_session import db
from utils import generate_random_color

class TimeTask(db.Model):
    __tablename__ = 'time-tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    description = db.Column(db.String, nullable=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time, nullable=True)
    duration = db.Column(db.Time, nullable=True)
    date = db.Column(db.Date)
    done = db.Column(db.Boolean, default=False)
    color = db.Column(db.String, default=generate_random_color)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship('User', back_populates='time_tasks')

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


class ShortTask(db.Model):
    __tablename__ = 'short-tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    description = db.Column(db.String, nullable=True)
    date = db.Column(db.Date)
    done = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship('User', back_populates='short_tasks')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "date": str(self.date),
            "done": self.done,
            "created_date": str(self.created_date),
        }


class CommonTask(db.Model):
    __tablename__ = 'common-tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    description = db.Column(db.String, nullable=True)
    done = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship('User', back_populates='common_tasks')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "done": self.done,
            "created_date": str(self.created_date),
        }