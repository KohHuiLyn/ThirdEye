from application import db
import datetime as dt
from sqlalchemy.orm import validates
from flask_login import  UserMixin 


class Video(UserMixin, db.Model):
    __tablename__='Videos'
    Video_id=db.Column