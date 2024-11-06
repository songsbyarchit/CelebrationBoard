from app import db    #get db from init
from werkzeug.security import generate_password_hash, check_password_hash    #for password hashing
from flask_login import UserMixin    #add login functionality to User model

class User(db.Model, UserMixin):    #inherit from UserMixin for login support
    id = db.Column(db.Integer, primary_key=True)    #basic model without security
    username = db.Column(db.String(80), unique=True, nullable=False)  #username must be unique
    email = db.Column(db.String(120), unique=True, nullable=False)    #email must be unique
    department = db.Column(db.String(50), nullable=False)    #required field
    job_title = db.Column(db.String(100), nullable=False)    #required field
    password_hash = db.Column(db.String(256), nullable=False)    #store only hashed passwords, never plain text

    def set_password(self, password):    #method to hash password before storing
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):    #method to verify password against hash
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'   #helps with debuging later