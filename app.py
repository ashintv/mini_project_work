import os
from flask import Flask, render_template, request, redirect, url_for, flash, session ,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

# Configure SQLite Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Directory to store profile pictures
UPLOAD_FOLDER = "static/profile_pics"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

db = SQLAlchemy(app)

# Ensure profile picture directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_pic = db.Column(db.String(200), nullable=True)  # Store file path

# Create the database
with app.app_context():
    db.create_all()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
app.route('/')
def index():
    return render_template('index.html')
    

def login_required(route_function):
    """Decorator to protect routes that require authentication."""
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("You need to log in first!", "warning")
            return redirect(url_for("login"))
        return route_function(*args, **kwargs)
    wrapper.__name__ = route_function.__name__
    return wrapper

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        file = request.files["profile_pic"]

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("signup"))

        # Hash the password before storing
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        # Handle file upload
        db_file_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)  # Save image
            db_file_path = f"profile_pics/{filename}"  # Store relative path

        # Create new user
        new_user = User(username=username, email=email, password=hashed_password, profile_pic=db_file_path)
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id  # Store user session
            session["username"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("profile"))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html")

@app.route("/profile")
@login_required
def profile():
    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

if __name__ == "__main__":
    app.run(debug=True)