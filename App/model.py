from App import db ,app,login_manager
from datetime import datetime
from flask_login import UserMixin
from App import bcrypt
# User Model

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model ,UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing ID
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    score = db.Column(db.Integer, default=0)  # Default score to avoid null values
    meetings = db.relationship("UserMeet", backref="user", lazy=True)
     
     
    # an attribute for the db to return password
    @property
    def password(self):
        return self.password
    
    #this attribut helps to hash the password
    @password.setter
    def password(self,plain_text_pass):
        self.password_hash=bcrypt.generate_password_hash(plain_text_pass).decode('utf-8')
    #function for checking the input during login
    def check_password_correction(self , attempted_password):
        return bcrypt.check_password_hash(self.password_hash,attempted_password)
    
    def is_authenticated(self):
        return True
           
        
    
# Meeting Model
class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Changed joinID to id
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    joinID = db.Column(db.String(50),nullable = False)  # Default value
    status = db.Column(db.String(10), default="active")
    participants = db.relationship("UserMeet", backref="meeting", lazy=True)

# UserMeet (Association Table)
class UserMeet(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    meet_id = db.Column(db.Integer, db.ForeignKey("meeting.id"), primary_key=True)
    score = db.Column(db.Integer, default=0)

# Global Ranking Model
class GlobalRanking(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    score = db.Column(db.Integer, default=0)
# Reset Database


#     print("⚠️ Dropping existing database...")
#     db.drop_all()  # Deletes all tables
#     print("✅ Database dropped.")

#     print("🚀 Creating new tables...")
#     db.create_all()  # Creates fresh tables
#     print("✅ Tables created.")

#     print("📌 Inserting sample data...")

#     # Insert Users
#     users = [
#         User(username="alice01", name="Alice", email="alice@example.com", role="Student", phone="1234567890", password=generate_password_hash("password123")),
#         User(username="bob02", name="Bob", email="bob@example.com", role="Teacher", phone="9876543210", password=generate_password_hash("password456")),
#         User(username="charlie03", name="Charlie", email="charlie@example.com", role="Student", phone="1122334455", password=generate_password_hash("password789")),
#         User(username="dave04", name="Dave", email="dave@example.com", role="Admin", phone="2233445566", password=generate_password_hash("adminpass")),
#         User(username="eve05", name="Eve", email="eve@example.com", role="Student", phone="3344556677", password=generate_password_hash("studentpass")),
#     ]
#     db.session.add_all(users)
#     db.session.commit()

#     # Insert Meetings
#     meetings = [
#         Meeting(title="AI Workshop", joinID="meet_001"),
#         Meeting(title="Data Science Seminar", joinID="meet_002"),
#         Meeting(title="Machine Learning Bootcamp", joinID="meet_003"),
#         Meeting(title="Deep Learning Webinar", joinID="meet_004"),
#         Meeting(title="Python Programming Class", joinID="meet_005"),
#     ]
#     db.session.add_all(meetings)
#     db.session.commit()

#     # Insert UserMeet Data (Link Users & Meetings)
#     user_meet_data = [
#         UserMeet(user_id=1, meet_id=1, score=85),
#         UserMeet(user_id=2, meet_id=2, score=90),
#         UserMeet(user_id=3, meet_id=3, score=70),
#         UserMeet(user_id=4, meet_id=4, score=95),
#         UserMeet(user_id=5, meet_id=5, score=80),
#     ]
#     db.session.add_all(user_meet_data)
#     db.session.commit()

#     # Insert Global Rankings
#     global_rankings = [
#         GlobalRanking(user_id=1, score=250),
#         GlobalRanking(user_id=2, score=300),
#         GlobalRanking(user_id=3, score=200),
#         GlobalRanking(user_id=4, score=350),
#         GlobalRanking(user_id=5, score=270),
#     ]
#     db.session.add_all(global_rankings)
#     db.session.commit()

#     print("✅ Sample data inserted successfully!")