import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager    #add login management
from dotenv import load_dotenv
from flask_mail import Mail
import pyotp
from datetime import datetime
from app.models import Post, User

load_dotenv()  # Load environment variables

app = Flask(__name__)

# File upload configuration
app.config['SUPER_ADMIN_EMAIL'] = os.environ.get('SUPER_ADMIN_EMAIL')
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'  # where files will be saved
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}  # allowed file types

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Security configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)    #use environment variable or generate random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'   #basic database setup

# Initialize extensions
db = SQLAlchemy(app)    #create the database
login_manager = LoginManager(app)    #create login manager instance
login_manager.login_view = 'login'    #set login page for @login_required
login_manager.login_message_category = 'info'    #set flash message category

@login_manager.user_loader    #tell flask-login how to load users
def load_user(id):
   return User.query.get(int(id))

# Create tables before importing routes and models
with app.app_context():
   from app import routes  #get the routes
   from app import models  #get the database models
   from app.models import User    #needed for load_user
   db.create_all()    #create all database tables

# Function to create sample data
def create_sample_data():
    admin = User(
        username='adminuser', 
        email='admin@example.com', 
        department='management',
        job_title='Admin',
        is_admin=True,
        mfa_otp='123456',  # Sample MFA OTP
        mfa_expiry=datetime.utcnow()
    )
    admin.set_password('Admin1234!')  # Meet password criteria
    
    user1 = User(
        username='user1', 
        email='user1@example.com', 
        department='engineering',
        job_title='Engineer',
        mfa_otp='654321',  # Sample MFA OTP
        mfa_expiry=datetime.utcnow()
    )
    user1.set_password('User1234!')  # Meet password criteria

    user2 = User(
        username='user2', 
        email='user2@example.com', 
        department='marketing',
        job_title='Marketer',
        mfa_otp='654321',  # Sample MFA OTP
        mfa_expiry=datetime.utcnow()
    )
    user2.set_password('User2345!')  # Meet password criteria

    # Add users to the database
    db.session.add(admin)
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    post1_user1 = Post(title='Post 1 by user1', content='Content of post 1 by user1', author=user1)
    post2_user1 = Post(title='Post 2 by user1', content='Content of post 2 by user1', author=user1, file_filename='dummyfile.pdf', file_path='uploads/dummyfile.pdf')
    
    post1_user2 = Post(title='Post 1 by user2', content='Content of post 1 by user2', author=user2)
    post2_user2 = Post(title='Post 2 by user2', content='Content of post 2 by user2', author=user2, file_filename='dummyfile2.pdf', file_path='uploads/dummyfile2.pdf')

    db.session.add(post1_user1)
    db.session.add(post2_user1)
    db.session.add(post1_user2)
    db.session.add(post2_user2)
    db.session.commit()

# Call the function to populate sample data
with app.app_context():
    create_sample_data()