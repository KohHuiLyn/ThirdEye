import email
from unicodedata import name
from webbrowser import get

from matplotlib.image import thumbnail
from application import app,db
from application.models import User,Students, RawVideo, Analysis, Parameters, Thumbnail
from datetime import datetime
from application.forms import  Back_Form, VideoForm, Feet_Form
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
# from flask_login import LoginManager,  login_user, login_required, logout_user, current_user
from flask import render_template, request, flash, json, jsonify,redirect,url_for, abort 
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

# Creates a default database for parameters
rows = db.session.query(func.count(Parameters.id)).scalar()
if (rows < 1):
    param_row = Parameters(Back_angle=45,Feet_length=50)
    db.session.add(param_row)
    db.session.commit()

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
def upload_file( ):
    if request.method=='POST':
        form=VideoForm()
        
        uploaded_file = request.files['file']      
        filename = secure_filename(uploaded_file.filename)
        if uploaded_file.filename != '': 
            title=form.title.data
            videoMethod=form.videoMethod.data #Back or Side
            # print("VIDEOMETHOD ",type(videoMethod))
            event=form.event.data
            uploaded_file.save(os.path.join('./application/static/rawvideo/',filename))
            DB_Filepath=os.path.join('./application/static/rawvideo/',filename)
            #ADD INTO DATABASE ( FILEPATH)
            DB_Filepath=str(DB_Filepath)
            # print("filepath ", DB_Filepath)
            videoEntry=RawVideo(video_path=DB_Filepath,date=datetime.utcnow(),Event=event)
            # Adding into database
            Rawvideo_id=add_entry(videoEntry)
            print(Rawvideo_id)
            name=str(title)+str(datetime.now().strftime("%m_%d_%Y_%H_%M_%S")) #should include an input variable.
            if int(videoMethod)==0:
                print("FWD BACK")
                backangles=mpEstimate().backAngle(DB_Filepath,name)#name supposed to be a variable
                
                # print("backangles ", backangles)
                mpEstimate().Backscreenshot('./application/static/analysedvideo/{name}.mp4'.format(name=name),name)#name supposed to be a variable.
                # entries = Entry.query.filter_by(user_id=userid)
                # print("length of backangles", len(backangles) )
                thumbnailentry=Thumbnail(RawVideo_id=Rawvideo_id,thumb_path='Thumbnail/frame_%d%s.jpg'%(0,name),Date=datetime.utcnow(),Event=event,Name=title)
                add_entry(thumbnailentry)  
                print("backangles is ",backangles)
                print("len is ",len(backangles))
                # If no backangles detected, insert record with length of 2, so that website won't confuse with Ball Release, which has length of 1.
                # Make the angles null.
                if len(backangles)==0:
                    for i in range(2):
                        analysisentry=Analysis(RawVideo_id=Rawvideo_id,Name=name,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="NO_PHOTO")
                        add_entry(analysisentry)
                for i in range (0,len(backangles),1):    
                    analysisentry=Analysis(RawVideo_id=Rawvideo_id,Name=name,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="Analysedphoto/frame_%d%s.jpg"%(i,name),Angle=int(backangles[i]))
                    add_entry(analysisentry)
                return redirect(url_for('analysis',videoid=Rawvideo_id))
            elif int(videoMethod)==1:
                print("FWD Timing")
            try:
                Timing=mpEstimate().timing(DB_Filepath,name)
                Timing=str(Timing)

                #perform mediapipe function
                mpEstimate().Timingscreenshot('./application/static/analysedvideo/{name}.mp4'.format(name=name),name,Timing)
                #Inputting file paths
                thmumbnailentry=Thumbnail(RawVideo_id=Rawvideo_id,thumb_path='Thumbnail/frame_%d%s.jpg'%(0,name),Date=datetime.utcnow(),Event=event,Name=title)
                add_entry(thmumbnailentry) 
                # If no timing, no photo file path
                if Timing == 'None':
                    analysisentry=Analysis(RawVideo_id=Rawvideo_id,Name=name,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="NO_PHOTO",Ball_release=Timing)
                    add_entry(analysisentry)
                # Else if have timing, got analysed photo filepath
                else:
                    analysisentry=Analysis(RawVideo_id=Rawvideo_id,Name=name,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="Analysedphoto/frame_%d%s.jpg"%(0,name),Ball_release=Timing)
                    add_entry(analysisentry)
                  
                return redirect(url_for('analysis',videoid=Rawvideo_id))
            except Exception as e:
                print("exception")
                print(e)
                abort(500) 
                return "video"
        
        
    

@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('500error.html'), 500
    

@app.route("/history",methods=['GET'])
def history():
    
    return render_template('history.html',title="Your History", history=gethistory())

def gethistory():
    try:
        video=Thumbnail.query.all()
        return video
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return 0

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

@app.route("/analysis/<videoid>",methods=['GET','POST'])
def analysis(videoid):
    
    return render_template('analysis.html',title="Your Analysis", analysis = get_latestAnalysis(video_id=videoid))

def get_latestAnalysis(video_id):
    try:
        # analysis = Analysis.query.all()
        analysis=Analysis.query.filter_by(RawVideo_id=video_id).all()
        # print(analysis[0].Video_filepath)
        return analysis
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return 0
