import email
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

db.create_all()

@app.route("/")
def home():
    return render_template('layout.html', title="Test")
def add_video(new_video):
    try:
        db.session.add(new_video)
        db.session.commit()
        print("success")
        return new_video.id
    except Exception as error:
        db.session.rollback()
        flash(error,"danger")

@app.route('/index',methods=['GET','POST'])
def video():
    form=VideoForm()
    video_method=form.videoMethod.data
    # files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('index.html',form=form,title="Home Page")



@app.route("/upload",methods=['GET','POST'])
def upload_file():
    
    if request.method=='POST':
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        
        
        if uploaded_file.filename != '':
            # uploaded_file.save(uploaded_file.filename)
            
            uploaded_file.save(os.path.join('./application/rawvideo/',filename))
            DB_Filepath=os.path.join('./application/rawvideo/',filename)
            #ADD INTO DATABASE ( FILEPATH)
            DB_Filepath=str(DB_Filepath)
            print(DB_Filepath)
            videoEntry=Video(video_path=DB_Filepath,date=datetime.utcnow(),Event="random")
            print(videoEntry)
            add_video(videoEntry)
            return redirect(url_for('video'))
    

    

@app.route("/history",methods=['GET'])
def history():
    return render_template('history.html',title="Your History")

@app.route("/login",methods=['GET'])
def login():
    return render_template('login.html',title="Login")
    
@app.route("/settings")
def settings():
    return render_template('settings.html', title="Settings")