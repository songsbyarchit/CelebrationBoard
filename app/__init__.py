import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager    #add login management

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'  # where files will be saved
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}  # allowed file types

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Your existing config
app.config['SECRET_KEY'] = 'dev'    #dont use this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'   #basic database setup

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