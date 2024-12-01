import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, logout_user
from dotenv import load_dotenv
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash

load_dotenv()

app = Flask(__name__)

app.config['SUPER_ADMIN_EMAIL'] = os.environ.get('SUPER_ADMIN_EMAIL')
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'postgresql://cel_board_db_user:8ETS9zWqSiBjgtzaocl45CAeSzM6Du2B@dpg-ct5nqrg8fa8c73bvu7g0-a.oregon-postgres.render.com/cel_board_db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from app.models import User
from app import routes

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Move this below app initialization
@app.before_first_request
def before_first_request():
    with app.test_request_context():
        logout_user()

    admin = User.query.filter_by(username='admin').first()
    if admin is None:
        admin = User(
            username='admin',
            email=os.environ.get('SUPER_ADMIN_EMAIL'),
            department='engineering',
            job_title='System Admin',
            password_hash=generate_password_hash(os.environ.get('ADMIN_PASSWORD')),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
    else:
        print("Admin user already exists!")

if __name__ == '__main__':
    app.run(debug=True)