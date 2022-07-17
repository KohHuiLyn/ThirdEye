from flask_wtf import FlaskForm
from wtforms import SelectField,StringField,PasswordField
from wtforms.validators import InputRequired, Email, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])



class VideoForm(FlaskForm):
    title = StringField('title')
    videoMethod =SelectField(u"Method",choices=[(0,"Side view"),(1,"Back View")],validators=[InputRequired()])