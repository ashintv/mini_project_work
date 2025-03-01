from flask_wtf import FlaskForm
from wtforms import StringField , PasswordField , SubmitField 
from wtforms.validators import Length , Email ,EqualTo , DataRequired ,ValidationError
from App.model import User ,Meeting

class RegisterUser(FlaskForm):
    def validate_username(self ,username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError("Username already exists! please try another username")
    def validate_email(self ,email_to_check):
        email = User.query.filter_by(email=email_to_check.data).first()
        if email:
            raise ValidationError("An account already using this email! please try another or login")
        
    username = StringField(label='User Name:' , validators=[Length(min=2 , max=30) , DataRequired()])
    email = StringField(label='Email:', validators=[Email() , DataRequired()])
    password1 = PasswordField(label="Password:",validators=[Length(min=6 , max=12) , DataRequired()])
    password2 = PasswordField(label="Confirm Password:",validators=[EqualTo('password1',message='Must be same as Password'), DataRequired()])
    submit  = SubmitField(label='Sign Up')
    
class LoginForm(FlaskForm):
    username = StringField(label='User Name:' , validators=[Length(min=2 , max=30) , DataRequired()])
    password = PasswordField(label="Password:",validators=[Length(min=6 , max=12) , DataRequired()])
    submit  = SubmitField(label='Sign In')
    
class JoinMeeting(FlaskForm): #create meeting form
    def validate_meeting(self,meeting_id):
        meeting = Meeting.query.filter_by(joinID = meeting_id)
        if meeting:
            raise ValidationError('Meeting already exist')
    title  = StringField(label='Meeting Name : ' , validators=[Length(min=4 , max=30) ,DataRequired() ])
    JoinID = StringField(label="Join Code : " , validators=[Length(min=4),DataRequired()])
    SubmitField = SubmitField(label='Create')
    
class Entermeeting(FlaskForm):
    def validate_meeting(self,meeting_id):
        meeting = Meeting.query.filter_by(joinID = meeting_id)
        if not  meeting:
            raise ValidationError('Meeting doed not exist')
    JoinID = StringField(label="Join Code : " , validators=[Length(min=4),DataRequired()])
    SubmitField = SubmitField(label='Join')