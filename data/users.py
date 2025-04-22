import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, index=True, unique=True, nullable=True)
    hashed_password = db.Column(db.String, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    time_zone = db.Column(db.String, nullable=True)
    avatar = db.Column(db.BLOB, nullable=True)

    time_tasks = db.relationship("TimeTask", back_populates='user')
    short_tasks = db.relationship("ShortTask", back_populates='user')
    common_tasks = db.relationship("CommonTask", back_populates='user')

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
            "time_zone": self.time_zone,
        }