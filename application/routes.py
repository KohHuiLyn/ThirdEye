import email
from webbrowser import get
from application import app
# from application.models import User,ImageTable
from datetime import datetime
# from application.forms import  LoginForm, RegisterForm
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