import email
from unicodedata import name
from webbrowser import get
from application import app,db
from application.models import User,Students, Video, Analysis 
from datetime import datetime
from application.forms import  VideoForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
# from flask_login import LoginManager,  login_user, login_required, logout_user, current_user
from flask import render_template, request, flash, json, jsonify,redirect,url_for 
from flask_cors import CORS, cross_origin
from sqlalchemy import text
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
import sqlite3
import cv2
import time
import math as m
import mediapipe as mp
from application.mediapipePY import mpEstimate
db.create_all()

#Creating of essential folders in static
analysedpath ='./application/static/analysedvideo'
AnalysedisExist = os.path.exists(analysedpath)
rawpath ='./application/static/rawvideo'
RawisExist = os.path.exists(rawpath)
if not AnalysedisExist:
    # Create a new directory because it does not exist 
    os.makedirs(analysedpath)
    print("Analysedvideo folder is created!")
if not RawisExist:
    # Create a new directory because it does not exist 
    os.makedirs(rawpath)
    print("rawvideo folder is created!")


@app.route('/',methods=['GET','POST'])
def video():
    form=VideoForm()
    video_method=form.videoMethod.data
    # files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('index.html',form=form,title="Home Page")


#Function for INSERT into database
def add_entry(new_entry):
    try:
        db.session.add(new_entry)
        db.session.commit()
        print("success")
        return new_entry.id
    except Exception as error:
        db.session.rollback()
        flash(error,"danger")

 


 
#Handling File upload, and mediapipe analysis
@app.route("/upload",methods=['GET','POST'])
def upload_file():
    if request.method=='POST':
        uploaded_file = request.files['file']      
        filename = secure_filename(uploaded_file.filename)
        if uploaded_file.filename != '': 
            uploaded_file.save(os.path.join('./application/static/rawvideo/',filename))
            DB_Filepath=os.path.join('./application/static/rawvideo/',filename)
            #ADD INTO DATABASE ( FILEPATH)
            DB_Filepath=str(DB_Filepath)
            print("filepath ", DB_Filepath)
            videoEntry=Video(video_path=DB_Filepath,date=datetime.utcnow(),Event="random")
            # Adding into database
            video_id=add_entry(videoEntry)
            name="Testing_"+str(datetime.now().strftime("%m_%d_%Y_%H_%M_%S")) #should include an input variable.
            
            backangles=mpEstimate().main(DB_Filepath,name)#name supposed to be a variable
            print("backangles ", backangles)
            
            mpEstimate().screenshot('./application/static/analysedvideo/{name}.mp4'.format(name=name),name)#name supposed to be a variable.
           
            # entries = Entry.query.filter_by(user_id=userid)
            print("length of backangles", len(backangles) )
            for i in range (0,len(backangles),1):
                
                # TO BE CHANGED TEMPORARILY
                #analysisentry=Analysis(Video_id=names[0],Video_filepath='./application/analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="Analysedphoto/frame_%s_%d.jpg"%(name,i),Angle=int(backangles[i]))
                analysisentry=Analysis(Video_id=video_id,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="Analysedphoto/frame_%d%s.jpg"%(i,name),Angle=int(backangles[i]))
                
                add_entry(analysisentry)
            
            return redirect(url_for('analysis',videoid=video_id))
    

    

@app.route("/history",methods=['GET'])
def history():
    return render_template('history.html',title="Your History")

@app.route("/login",methods=['GET'])
def login():
    return render_template('login.html',title="Login")
    
@app.route("/settings",methods=['GET'])
def settings():
    return render_template('settings.html', title="Settings")

@app.route("/analysis/<videoid>",methods=['GET','POST'])
def analysis(videoid):
    
    return render_template('analysis.html',title="Your Analysis", analysis = get_latestAnalysis(video_id=videoid))

def get_latestAnalysis(video_id):
    try:
        # analysis = Analysis.query.all()
        analysis=Analysis.query.filter_by(Video_id=video_id).all()
        # print(analysis[0].Video_filepath)
        return analysis
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return 0
