import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_mail import Mail
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()


# Initialize Flask app
app = Flask(__name__)

# App configurations
app.config['SUPER_ADMIN_EMAIL'] = os.environ.get('SUPER_ADMIN_EMAIL')
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'postgresql://arsachde:Karnal.123@localhost/celebrationboard'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Set in .env
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Set in .env
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
mail = Mail(app)

# Import models after db initialization
from app import routes
from app import models

# Flask-Login user loader function
@login_manager.user_loader
def load_user(id):
    from app.models import User  # Move import here to avoid circular import
    return User.query.get(int(id))

# Create the admin user by default if it doesn't exist
with app.app_context():
    db.create_all()  # Create all database tables

    # Check if admin exists, if not, create one
    from app.models import User  # Import models here to avoid circular import
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', email=os.environ.get('SUPER_ADMIN_EMAIL'), department='Engineering', job_title='System Admin')
        admin_user.set_password(os.environ.get('ADMIN_PASSWORD'))
        admin_user.is_admin = True
        db.session.add(admin_user)
        db.session.commit()