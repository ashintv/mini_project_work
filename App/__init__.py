from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

app.config["SECRET_KEY"] = "your_secret_key_here"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///mydatabase.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)  # ✅ Initialize Bcrypt here
login_manager = LoginManager(app)
login_manager.login_view = "login"
migrate = Migrate(app, db)

# Move imports to the bottom to avoid circular import issues
from App import routes, model