import email
from unicodedata import name
from webbrowser import get
from matplotlib.image import thumbnail
from application import app,db
from application.models import Users,Students, RawVideo, Analysis, Parameters, Thumbnail
from datetime import datetime
from application.forms import  Back_Form, LoginForm, VideoForm, Feet_Form, LoginForm,RegisterForm, SearchForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager,  login_user, login_required, logout_user, current_user
from flask import render_template, request, flash, json, jsonify,redirect,url_for, Markup, Response,render_template_string
from flask_cors import CORS, cross_origin
from sqlalchemy import text, func,desc, not_, and_
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
import redis
from rq import Queue
from rq.job import Job
from application.mediapipePY import mpEstimate
import ffmpy
from worker import conn
db.create_all()
q=Queue(connection=conn)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = 'extremely secretive!'

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
    #print("fn start")
    if Users.query.filter_by(username="admin").first() is None:
        print("adding user")
        hashed_password1 = generate_password_hash("Password", method='sha256')
        userentry1=Users(username="admin",email="admin@gmail.com",password=hashed_password1)
        add_entry(userentry1)
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


# Main page prompt to log in, after logging in it will redirect to video page
@app.route("/",methods=['GET','POST'])
def login():
    form=LoginForm()
    # Form to validate if account exist. If it does not exist, redirect back to logi n bage
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
# Logout function
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
@app.route('/video',methods=['GET','POST'])
def video():
    form=VideoForm()
    # files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('index.html',form=form,title="Home Page")

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


def analyseBack(DB_Filepath,name,Rawvideo_id,event,title,description_content, current_user):
    backangles=mpEstimate().backAngle(DB_Filepath,name)
    print(backangles)
    if(description_content==None):
        description_content=""
    thumbnailentry=Thumbnail(User_id=current_user,RawVideo_id=Rawvideo_id,thumb_path='Thumbnail/frame_%d%s.jpg'%(0,name),Date=datetime.utcnow(),Event=event,Name=title)
    add_entry(thumbnailentry)
   # If no backangles detected, insert record with length of 2, so that website won't confuse with Ball Release, which has length of 1.
                # Make the angles null.
    if len(backangles)==0:
        for i in range(2):
            analysisentry=Analysis(User_id=current_user,RawVideo_id=Rawvideo_id,Name=name,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="NO_PHOTO", Description=description_content)
            add_entry(analysisentry)
    for i in range (0,len(backangles),1):    
        analysisentry=Analysis(User_id=current_user,RawVideo_id=Rawvideo_id,Name=name,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="Analysedphoto/frame_%d%s.jpg"%(i,name),Angle=int(backangles[i]),Description=description_content)
        add_entry(analysisentry)
    ff=ffmpy.FFmpeg(
        inputs={'./application/static/analysedvideo/{name}.avi'.format(name=name):None},
        outputs={'./application/static/analysedvideo/{name}.mp4'.format(name=name):'-c:v libx264'}
    )
    ff.run()
    os.remove('./application/static/analysedvideo/{name}.avi'.format(name=name))
    mpEstimate().Backscreenshot('./application/static/analysedvideo/{name}.mp4'.format(name=name),name)
    
def analyseTiming(DB_Filepath,name,Rawvideo_id,event,title,description_content, current_user):
    Timing=mpEstimate().timing(DB_Filepath,name)
    Timing=str(Timing)
    #perform mediapipe function 
    ff=ffmpy.FFmpeg(
        inputs={'./application/static/analysedvideo/{name}.avi'.format(name=name):None},
        outputs={'./application/static/analysedvideo/{name}.mp4'.format(name=name):'-c:v libx264'}
    )
    ff.run()
    mpEstimate().Timingscreenshot('./application/static/analysedvideo/{name}.mp4'.format(name=name),name,Timing)
    os.remove('./application/static/analysedvideo/{name}.avi'.format(name=name))
    #Inputting file paths
    thmumbnailentry=Thumbnail(User_id=current_user,RawVideo_id=Rawvideo_id,thumb_path='Thumbnail/frame_%d%s.jpg'%(0,name),Date=datetime.utcnow(),Event=event,Name=title)
    add_entry(thmumbnailentry)  
    if Timing == 'None':
            analysisentry=Analysis(User_id=current_user,RawVideo_id=Rawvideo_id,Name=name,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="NO_PHOTO",Ball_release=Timing,Description=description_content)
            add_entry(analysisentry)
                # Else if have timing, got analysed photo filepath
    else:
        analysisentry=Analysis(User_id=current_user,RawVideo_id=Rawvideo_id,Name=name,Video_filepath='analysedvideo/{name}.mp4'.format(name=name),Photo_filepath="Analysedphoto/frame_%d%s.jpg"%(0,name),Ball_release=Timing,Description=description_content)
        add_entry(analysisentry) 


        
def get_template(refresh=False):
    # Search function
    search = SearchForm()
    if request.method == 'GET' and search.validate_on_submit():
        return redirect((url_for('search_results', query=search.search.data)))  # or what you want
    return render_template('history.html', refresh=refresh,form=VideoForm(),search=search, history=gethistory())    
    
 
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
            event=form.event.data
            description=form.description.data
            uploaded_file.save(os.path.join('./application/static/rawvideo/',filename))
            DB_Filepath=os.path.join('./application/static/rawvideo/',filename)
            #ADD INTO DATABASE ( FILEPATH)
            DB_Filepath=str(DB_Filepath)
            videoEntry=RawVideo(User_id=current_user.id,video_path=DB_Filepath,date=datetime.utcnow(),Event=event)
            # Adding into database
            Rawvideo_id=add_entry(videoEntry)
            title=re.sub("[\s/]","-",title)
            name=str(title)+str(datetime.now().strftime("%m_%d_%Y_%H_%M_%S")) 
            if int(videoMethod)==0:
                print("FWD BACK")
                job=q.enqueue(analyseBack,args=(DB_Filepath,name,Rawvideo_id,event,title,description,current_user.id),job_timeout="2h")
                
                
            elif int(videoMethod)==1:
                print("FWD Timing")
                job=q.enqueue(analyseTiming,args=(DB_Filepath,name,Rawvideo_id,event,title,description,current_user.id),job_timeout="2h")
                                
            return redirect(url_for('result',id=job.id,video_id=Rawvideo_id))


@app.route('/result/<string:id>/<string:video_id>')
def result(id,video_id):
    job = Job.fetch(id, connection=conn)
    status = job.get_status()
    if status in ['queued', 'started', 'deferred', 'failed']:
        return get_template( refresh=True)
    elif status == 'finished':
        flash(Markup(f'Analysis Complete, go to <a href="/history">History page</a> or click <a href="/analysis/{video_id}">here</a>'))
        # If this is a string, we can simply return it:
        return get_template()
    
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

# History and search videos
@app.route("/history",methods=['GET'])
@app.route('/history/<filter>')
@login_required
def history(filter=None):
    search = SearchForm()
    if request.method == 'GET' and search.validate_on_submit():
        return redirect((url_for('search_results', query=search.search.data)))  # or what you want
    if filter:
        if filter == "t":
            return render_template('history.html',title="Your History", history=getTiming(), search=search, vidType="Timing")
        elif filter =="ba":
            return render_template('history.html',title="Your History", history=getBA(), search=search, vidType="Back Angle")
        elif filter == None:
            return render_template('history.html',title="Your History", history=gethistory(), search=search, vidType="All")

    return render_template('history.html',title="Your History", history=gethistory(), search=search, vidType="All")
def getTiming():
    try:
        timingVids = db.session.query(Thumbnail).join(Analysis,Analysis.RawVideo_id==Thumbnail.RawVideo_id).filter(and_(Analysis.Ball_release.is_not(None), Analysis.User_id==current_user.id)).order_by(Thumbnail.Date.desc()).all()
        return timingVids
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return []
def getBA():
    try:
        baVids = db.session.query(Thumbnail).join(Analysis,Analysis.RawVideo_id==Thumbnail.RawVideo_id).filter(and_(Analysis.Angle.is_not(None), Analysis.User_id==current_user.id)).order_by(Thumbnail.Date.desc()).all()
        return baVids
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return []

def gethistory():
    try:
        video=Thumbnail.query.filter_by(User_id=current_user.id).all()
        return video
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return []
    
@app.route("/settings",methods=['GET'])
def settings():  
    back_form = Back_Form()
    feet_form = Feet_Form()
    update = Parameters.query.get_or_404(1)
    db_backangle = update.Back_angle
    db_feetlength = update.Feet_length
    current_username = current_user.username
    current_useremail = current_user.email
    return render_template('settings.html', title="Settings",
                                             back_form = back_form, 
                                             feet_form = feet_form, 
                                             db_backangle = db_backangle, 
                                             db_feetlength = db_feetlength,
                                             current_username = current_username,
                                             current_useremail = current_useremail)

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
    
    return render_template('analysis.html',title="Your Analysis", analysis = get_latestAnalysis(video_id=videoid),
                            video_info = get_relatedVideo(video_id=videoid))

def get_latestAnalysis(video_id):
    try:
        analysis=Analysis.query.filter_by(RawVideo_id=video_id,User_id=current_user.id).all()
        return analysis
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return []
def get_relatedVideo(video_id):
    try:
        video_info=RawVideo.query.filter_by(id=video_id, User_id=current_user.id).all()
        return video_info
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return []