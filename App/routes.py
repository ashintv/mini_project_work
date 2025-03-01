from flask import render_template , request ,redirect , url_for ,flash 
from App import app, db ,socketio
from App.model import Meeting ,User ,UserMeet 
from App.prediction import process_emotion_gaze
import threading 
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from App import forms
from flask_login import login_user ,logout_user , login_required , current_user
import plotly.express as px
from markupsafe import escape

@app.route('/')
@app.route('/home')
def main():
    #return render_template('profile.html', graph_html=graph_html)
    return render_template('landing.html' )



@app.route('/Profile')
@login_required
def dashboard():
    scores = [10, 20, 30, 40, current_user.score]
    labels = ["Jan", "Feb", "Mar", "Apr", "Your Score"]

    # Create a Plotly Bar Chart
    fig = px.bar(x=labels, y=scores, title="User Score Progress", labels={'x': 'Month', 'y': 'Score'})
    graph_html = fig.to_html(full_html=False)  # Convert to embeddable HTML

    
    return render_template('dashboard.html' ,graph_html=graph_html)

@app.route('/register', methods=["GET", "POST"])
def RegisterUser():
    form = forms.RegisterUser()
    if form.validate_on_submit():
        user_to_register = User(username =form.username.data,
                                email = form.email.data,
                                password= form.password1.data)
        db.session.add(user_to_register)
        db.session.commit()
        attempted_user = User.query.filter_by(username=form.username.data).first()
        login_user(attempted_user)
        return redirect(url_for('dashboard'))
    if form.errors != {}:
        for err in form.errors.values():
            flash(f'Error in Creating user {err}', category='danger')
    return render_template('register.html',form = form)



@app.route('/login', methods=["GET", "POST"])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password = form.password.data):
            login_user(attempted_user)
            flash(f'Login Succesfull {form.username.data}',category='success')
            return redirect(url_for('dashboard'))
        else:
            flash(f'Username or password is incorrect',category='danger')
    return render_template('login.html',form = form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout Successfull!' , category='success')
    return redirect(url_for('main'))


@app.route('/create' , methods = ['GET','POST'])
@login_required
def create_meet():
    form = forms.JoinMeeting()
    if form.validate_on_submit():
        meeting_to_create = Meeting(
            title = form.title.data,
            joinID  = form.JoinID.data
        )
        db.session.add(meeting_to_create)
        db.session.commit()
        meeting = Meeting.query.filter_by(joinID = form.JoinID.data).first()
        flash('Meeting Created succesfully')
        return redirect(url_for('meeting_dashboard', meeting_id=meeting.id))
    if form.errors != {}:
        for err in form.errors.values():
            flash(f'Error in Creating user {err}', category='danger')
    return render_template('create_meeting.html' ,  form=form)

@app.route("/join" ,methods = ['GET' ,'POST'])
@login_required
def join_meet():
    form = forms.Entermeeting()
    if form.validate_on_submit():
        meeting = Meeting.query.filter_by(joinID = form.JoinID.data).first()
        rejoin = UserMeet.query.filter_by(user_id = current_user.id).first()
        if rejoin is None:
            
            user_joined = UserMeet(
                user_id = current_user.id,
                meet_id = meeting.id
            )
            db.session.add(user_joined)
            db.session.commit()
            flash('Joined meeting successfully' , category='success')
        return redirect(url_for('meeting_dashboard' , meeting_id=meeting.id ))
    
    if form.errors != {}:
        for err in form.errors.values():
            flash(f'Error in Creating user {err}', category='danger')
    return render_template('joinform.html' , form = form)

@app.route("/meeting_dashboard/<int:meeting_id>")
@login_required
def meeting_dashboard(meeting_id):
    # Fetch users who joined this meeting
    data = (
        db.session.query(User.username, UserMeet.score)
        .join(UserMeet, User.id == UserMeet.user_id)
        .filter(UserMeet.meet_id == meeting_id)
        .all()
    )


    return render_template('Meeting.html' , data=data)

def end_meeting(meeting_id):
    meeting = Meeting.query.get(meeting_id)
    if meeting:
        meeting.status = "ended"
        db.session.commit()
        return True
    return False

