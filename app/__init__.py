import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_mail import Mail
from flask_migrate import Migrate
import psycopg2

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

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
mail = Mail(app)

# Initialize session for MFA
app.config['SESSION_TYPE'] = 'filesystem'

# Add the PostgreSQL connection here using psycopg2
connection = psycopg2.connect(
    host="dpg-ct575fqlqhvc73a7c7a0-a",  # Hostname from Render
    port="5432",  # Default PostgreSQL port
    dbname="celebrationboard",  # Database name
    user="celebrationboard_user",  # Username
    password=os.environ.get('DB_PASSWORD')  # Make sure to set password in .env
)