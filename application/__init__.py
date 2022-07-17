from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_talisman import Talisman
import os
#create the Flask app

app = Flask(__name__)
Bootstrap(app)
CORS(app)

# Wrap Flask app with Talisman
# Talisman(app, content_security_policy=None)

app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)
from application import routes