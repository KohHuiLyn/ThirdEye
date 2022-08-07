import email
from unicodedata import name
from webbrowser import get

from matplotlib.image import thumbnail
from application import app,db
from application.models import Users,Students, RawVideo, Analysis, Parameters, Thumbnail
from datetime import datetime
from application.forms import  Back_Form, VideoForm, Feet_Form, SearchForm, LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager,  login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
# from flask_login import LoginManager,  login_user, login_required, logout_user, current_user
from flask import render_template, request, flash, json, jsonify,redirect,url_for, abort 
from flask_cors import CORS, cross_origin
from sqlalchemy import text, func, desc, not_, and_
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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

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

#Creating Default User
def create_users():
    print("fn start")
    if Users.query.filter_by(username="admin").first() is None:
        print("adding user")
        hashed_password1 = generate_password_hash("Password", method='sha256')
        userentry1=Users(username="admin",email="admin@gmail.com",password=hashed_password1)
        add_entry(userentry1)
        userentry2=Users(username="admin2",email="admin2@gmail.com",password=hashed_password1) 
        add_entry(userentry2)
create_users()

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

# Login Page
@app.route('/',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        print("validated")
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash(f"Login!","success")
                print(current_user.id)
                return redirect(url_for('video'))

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html',form=form)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
# Home page (upload video)
@app.route('/video',methods=['GET','POST'])
@login_required
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

# Register page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = Users(username=form.username.data, email=form.email.data, password=hashed_password)
        add_entry(new_user)
        flash(f"User Created")
        return render_template('signup.html', form=form)
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

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
            description=form.description.data
            uploaded_file.save(os.path.join('./application/static/rawvideo/',filename))
            DB_Filepath=os.path.join('./application/static/rawvideo/',filename)
            #ADD INTO DATABASE ( FILEPATH)
            DB_Filepath=str(DB_Filepath)
            # print("filepath ", DB_Filepath)
            videoEntry=RawVideo(User_id=current_user.id, video_path=DB_Filepath,date=datetime.utcnow(),Event=event)
            # Adding into database
            Rawvideo_id=add_entry(videoEntry)
            print(Rawvideo_id)
            description_conent = str(description)
            name=str(title)+str(datetime.now().strftime("%m_%d_%Y_%H_%M_%S")) #should include an input variable.
            if int(videoMethod)==0:
                print("FWD BACK")
                backangles=mpEstimate().backAngle(DB_Filepath,name)#name supposed to be a variable
                
                # print("backangles ", backangles)
                mpEstimate().Backscreenshot('./application/static/analysedvideo/{name}.mp4'.format(name=name),name)#name supposed to be a variable.
                # entries = Entry.query.filter_by(user_id=userid)
                # print("length of backangles", len(backangles) )
                thumbnailentry=Thumbnail(User_id=current_user.id,RawVideo_id=Rawvideo_id,thumb_path='Thumbnail/frame_%d%s.jpg'%(0,name),Date=datetime.utcnow(),Event=event,Name=title)
                add_entry(thumbnailentry)  
                print("backangles is ",backangles)
                print("len is ",len(backangles))
                # If no backangles detected, insert record with length of 2, so that website won't confuse with Ball Release, which has length of 1.
                # Make the angles null.
                if len(backangles)==0:
                    for i in range(2):
                        analysisentry=Analysis(User_id=current_user.id,RawVideo_id=Rawvideo_id,Name=name,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="NO_PHOTO", Description=description_conent)
                        add_entry(analysisentry)
                for i in range (0,len(backangles),1):    
                    analysisentry=Analysis(User_id=current_user.id,RawVideo_id=Rawvideo_id,Name=name,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="Analysedphoto/frame_%d%s.jpg"%(i,name),Angle=int(backangles[i]),Description=description_conent)
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
                thmumbnailentry=Thumbnail(User_id=current_user.id,RawVideo_id=Rawvideo_id,thumb_path='Thumbnail/frame_%d%s.jpg'%(0,name),Date=datetime.utcnow(),Event=event,Name=title)
                add_entry(thmumbnailentry) 
                # If no timing, no photo file path
                if Timing == 'None':
                    analysisentry=Analysis(User_id=current_user.id,RawVideo_id=Rawvideo_id,Name=name,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="NO_PHOTO",Ball_release=Timing,Description=description_conent)
                    add_entry(analysisentry)
                # Else if have timing, got analysed photo filepath
                else:
                    analysisentry=Analysis(User_id=current_user.id,RawVideo_id=Rawvideo_id,Name=name,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="Analysedphoto/frame_%d%s.jpg"%(0,name),Ball_release=Timing,Description=description_conent)
                    add_entry(analysisentry)
                  
                return redirect(url_for('analysis',videoid=Rawvideo_id))
            except Exception as e:
                print("exception")
                print(e)
                abort(500) 
                return "video"
        
# Not found
@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('500error.html'), 500

# History and search videos
@app.route("/history",methods=['GET'])
@app.route('/history/<filter>')
@login_required
def history(filter=None):

        # if filter == "ba":
    # Search function
    search = SearchForm()
    if request.method == 'GET' and search.validate_on_submit():
        return redirect((url_for('search_results', query=search.search.data)))  # or what you want
    if filter:
        if filter == "t":
            history = getTiming()  
            return render_template('history.html',title="Your History", history=history, search=search, vidType="Timing")
        elif filter =="ba":
            history = getBA()
            return render_template('history.html',title="Your History", history=history, search=search, vidType="Back Angle")

        elif filter == None:
            return render_template('history.html',title="Your History", history=getBA(), search=search, vidType="All")

    return render_template('history.html',title="Your History", history=gethistory(), search=search, vidType="All")
def getTiming():
    try:
        timingVids = db.session.query(Thumbnail).join(Analysis,Analysis.RawVideo_id==Thumbnail.RawVideo_id).filter(and_(Analysis.Ball_release.is_not(None), Analysis.User_id==current_user.id)).order_by(Thumbnail.Date.desc()).all()
        return timingVids
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return 0
def getBA():
    try:
        baVids = db.session.query(Thumbnail).join(Analysis,Analysis.RawVideo_id==Thumbnail.RawVideo_id).filter(and_(Analysis.Angle.is_not(None), Analysis.User_id==current_user.id)).order_by(Thumbnail.Date.desc()).all()
        return baVids
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return 0
@app.route("/search", methods=["POST"])
def search():
    search = SearchForm()
    if search.validate_on_submit():
        search = search.searched.data
        searchStr = "%{}%".format(search)
        return render_template("search.html", form=search, search = search, searchVideos= getSearch(searchStr))
def getSearch(searchStr):
    try:
        video=Thumbnail.query.filter(Thumbnail.Name.like(searchStr)).all()
        return video
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return 0
# Get all history
def gethistory():
    try:
        video=Thumbnail.query.filter_by(User_id=current_user.id).order_by(Thumbnail.Date.desc()).all()
        return video
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return 0
    
@app.route("/settings",methods=['GET'])
@login_required
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

# Analysis page
@app.route("/analysis/<videoid>",methods=['GET','POST'])
@login_required
def analysis(videoid):
    
    return render_template('analysis.html',title="Your Analysis", analysis = get_latestAnalysis(video_id=videoid),
                            video_info = get_relatedVideo(video_id=videoid))
def get_latestAnalysis(video_id):
    try:
        # analysis = Analysis.query.all()
        analysis=Analysis.query.filter_by(RawVideo_id=video_id,User_id=current_user.id).all()
        # print(analysis[0].Video_filepath)
        return analysis
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return 0
def get_relatedVideo(video_id):
    try:
        video_info=RawVideo.query.filter_by(id=video_id, User_id=current_user.id).all()
        return video_info
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return 0