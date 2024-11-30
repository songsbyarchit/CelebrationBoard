import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize db and login manager before importing models
app.config['SUPER_ADMIN_EMAIL'] = os.environ.get('SUPER_ADMIN_EMAIL')
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import models after db initialization
from app import routes
from app import models

@login_manager.user_loader
def load_user(id):
   return User.query.get(int(id))

# Create the admin user by default
with app.app_context():
    db.create_all()  # Create all database tables

    # Check if admin exists, if not, create one
    from app.models import User  # Move import here to avoid circular import
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', email='arsachde@cisco.com', department='Engineering', job_title='System Admin')
        admin_user.set_password('Karnal.123')
        admin_user.is_admin = True
        db.session.add(admin_user)
        db.session.commit()