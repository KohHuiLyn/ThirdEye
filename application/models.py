from application import db
import datetime as dt
from sqlalchemy.orm import validates
from flask_login import  UserMixin 

class User(UserMixin,db.Model):
    __tablename__ = 'Users'
 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String,nullable=False)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    Videos=db.relationship('Video',backref='user')

class Students(UserMixin,db.Model):
    __tablename__='Students'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name=db.Column(db.String,nullable=False)
    Videos=db.relationship('Video',backref='Student')
class Video(UserMixin, db.Model):
    __tablename__='Videos'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    User_id=db.Column(db.Integer,db.ForeignKey('Users.id'))
    Student_id=db.Column(db.Integer,db.ForeignKey('Students.id'))
    video_path=db.Column(db.String)
    date=db.Column(db.DateTime,nullable=False)
    Event=db.Column(db.String,nullable=False) #where was this event
    Analysis=db.relationship('Analysis',backref='Video')
    
class Analysis(UserMixin,db.Model):
    __tablename__='Analysis'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    Video_id=db.Column(db.Integer,db.ForeignKey('Videos.id'))
    Angle=db.Column(db.Integer,nullable=False)
    Ball_release=db.Column(db.String,nullable=False)
    Error_Count=db.Column(db.Integer)