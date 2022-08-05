from flask_wtf import FlaskForm
from wtforms import SelectField,StringField,PasswordField,IntegerField,SubmitField
from wtforms.validators import InputRequired, Email, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

class SearchForm(FlaskForm):
    searched = StringField('Search', [InputRequired()])
    submit = SubmitField("Search")

class VideoForm(FlaskForm):
    title = StringField('Title')
    videoMethod =SelectField(u"Method",choices=[(0,"Back Angle"),(1,"Timing")],validators=[InputRequired()])
    # event= StringField('Event')
    event = SelectField(u"Method",choices=[("Planet Bowl","Planet Bowl"),("Sonic Bowl","Sonic Bowl")],validators=[InputRequired()])
    submit = SubmitField("Upload")

class Back_Form(FlaskForm):
    back_angle = IntegerField("Back_angle", validators = [InputRequired()])
    submit = SubmitField("Submit")
class Feet_Form(FlaskForm):
    feet_length = StringField("Feet_length",validators=[InputRequired()])
    submit = SubmitField("Submit")
