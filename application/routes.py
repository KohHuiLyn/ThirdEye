import email
from unicodedata import name
from webbrowser import get
from application import app,db
from application.models import User,Students, Video, Analysis, Parameters
from datetime import datetime
from application.forms import  Back_Form, VideoForm, Feet_Form
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
# from flask_login import LoginManager,  login_user, login_required, logout_user, current_user
from flask import render_template, request, flash, json, jsonify,redirect,url_for 
from flask_cors import CORS, cross_origin
from sqlalchemy import text, func
import pathlib, os
import requests
import keras.models
from PIL import Image, ImageOps
from keras.preprocessing import image
import numpy as np
import re
import base64
import tempfile
import numpy as np
import sqlite3 as sql
import cv2
import time
import math as m
import mediapipe as mp
from application.mediapipePY import mpEstimate
db.create_all()

rows = db.session.query(func.count(Parameters.id)).scalar()
if (rows < 1):
    param_row = Parameters(Back_angle=45,Feet_length=50)
    db.session.add(param_row)
    db.session.commit()

# @app.route("/")
# def home():
#     return render_template('layout.html', title="Test")

@app.route('/',methods=['GET','POST'])
def video():
    form=VideoForm()
    video_method=form.videoMethod.data
    # files = os.listdir(app.config['UPLOAD_PATH']) so the syntax is theHTMLname = theRoutes.pyName
    return render_template('index.html',form=form,title="Home Page")


def add_video(new_video):
    try:
        db.session.add(new_video)
        db.session.commit()
        print("success")
        return new_video.id
    except Exception as error:
        db.session.rollback()
        flash(error,"danger")

 
def add_analysedVideo(new_video):
    try:
        db.session.add(new_video)
        db.session.commit()
        print("success")
        return new_video.id
    except Exception as error:
        db.session.rollback()
        flash(error,"danger")

 

@app.route("/upload",methods=['GET','POST'])
def upload_file():
    if request.method=='POST':
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        
        
        if uploaded_file.filename != '':
            # uploaded_file.save(uploaded_file.filename)
            #NEED TO ADD A WAY TO ENTER NAME FOR THE VIDEO THEN CONCAT WITH FILENAME
            uploaded_file.save(os.path.join('./application/rawvideo/',filename))
            DB_Filepath=os.path.join('./application/rawvideo/',filename)
            #ADD INTO DATABASE ( FILEPATH)
            DB_Filepath=str(DB_Filepath)
            print(DB_Filepath)
            videoEntry=Video(video_path=DB_Filepath,date=datetime.utcnow(),Event="random")
            # Adding into database
            add_video(videoEntry)
            name="Testing "+str(datetime.now().strftime("%d-%m-%Y"))
            
            backangles=mpEstimate().main(DB_Filepath,name)#name supposed to be a variable
            print(backangles)
            
            mpEstimate().screenshot('./application/analysedvideo/{name}.mp4'.format(name=name),name)#name supposed to be a variable.
           
            # entries = Entry.query.filter_by(user_id=userid)
            
            
            sql=text("SELECT Videos.id FROM Videos ORDER BY id DESC LIMIT 1")
            UsefulID=db.engine.execute(sql)
            names=[row[0] for row in UsefulID]
            print(names[0])            
            print(len(backangles))
            print(int(backangles[0]))
            for i in range (0,len(backangles),1):
                print("i ",i)
                # TO BE CHANGED TEMPORARILY
                #analysisentry=Analysis(Video_id=names[0],Video_filepath='./application/analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="Analysedphoto/frame_%s_%d.jpg"%(name,i),Angle=int(backangles[i]))
                analysisentry=Analysis(Video_id=names[0],Video_filepath='./application/analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="Analysedphoto/frame_%d.jpg"%(i),Angle=int(backangles[i]))
                print(analysisentry)
                add_analysedVideo(analysisentry)
            # test=Analysis(Video_id=1,Video_filepath="EVERYTHING",Photo_filepath="SUCKS",Angle=2)
            # print(backangles[2])
            # add_analysedVideo(test)
            return redirect(url_for('analysis'))
    

    

@app.route("/history",methods=['GET'])
def history():
    return render_template('history.html',title="Your History")

@app.route("/login",methods=['GET'])
def login():
    return render_template('login.html',title="Login")
    
@app.route("/settings",methods=['GET'])
def settings():  
    back_form = Back_Form()
    feet_form = Feet_Form()
    update = Parameters.query.get_or_404(1)
    db_backangle = update.Back_angle
    db_feetlength = update.Feet_length
    return render_template('settings.html', title="Settings",
                                             back_form = back_form, 
                                             feet_form = feet_form, 
                                             db_backangle = db_backangle, 
                                             db_feetlength = db_feetlength)

@app.route('/edit_back', methods=['GET','POST'])
def back_param():
    back_form = Back_Form() 
    feet_form = Feet_Form()
    update = Parameters.query.get_or_404(1)
    if request.method == 'POST': 
        update.Back_angle = request.form['back_angle']
        try:
            db.session.commit()
            flash("Updated Successfully")
            return render_template("settings.html",
                                    back_form=back_form, feet_form = feet_form,
                                    update=update)
        except:
            flash("Error!")
            return render_template("settings.html",
                                    back_form=back_form,feet_form = feet_form,
                                    update=update)
    else:
        return render_template("settings.html",
                                    back_form=back_form,feet_form = feet_form,
                                    update=update)
                                    

@app.route('/edit_feet', methods=['GET','POST'])
def feet_param():
    feet_form = Feet_Form() 
    back_form = Back_Form() 
    update = Parameters.query.get_or_404(1)
    if request.method == 'POST': 
        update.Feet_length = request.form['feet_length']
        try:
            db.session.commit()
            flash("Updated Successfully")
            return render_template("settings.html",
                                    feet_form=feet_form, back_form = back_form,
                                    update=update)
        except:
            flash("Error!")
            return render_template("settings.html",
                                    feet_form=feet_form, back_form = back_form,
                                    update=update)
    else:
        return render_template("settings.html",
                                    feet_form=feet_form, back_form = back_form,
                                    update=update)

@app.route("/analysis",methods=['GET'])
def analysis():
    
    return render_template('analysis.html',title="Your Analysis", analysis = get_latestAnalysis())

def get_latestAnalysis():
    try:
        analysis = Analysis.query.all()
        return analysis
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return 0
