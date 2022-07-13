import email
from webbrowser import get
from application import app
# from application.models import User,ImageTable
from datetime import datetime
from application.forms import  VideoForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
# from flask_login import LoginManager,  login_user, login_required, logout_user, current_user
from flask import render_template, request, flash, json, jsonify,redirect,url_for 
# from flask_cors import CORS, cross_origin
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

@app.route("/")
def home():
    return render_template('layout.html', title="Test")

# @app.route("/history")
# def home():
#     return render_template('history.html', title="Test")
@app.route("/index",methods=['GET','POST'])
def video():
    form=VideoForm()
    video_method=form.videoMethod.data
    print(video_method)
    return render_template('index.html',form=form,title="Home Page",method=0)

# @app.route("/SelectMethod",methods=['Get','POST'])
# def video():

@app.route("/history",methods=['GET'])
def history():
    return render_template('history.html',title="Your History")

@app.route("/login",methods=['GET'])
def login():
    return render_template('login.html',title="Login")
    
@app.route("/settings")
def settings():
    return render_template('settings.html', title="Test")