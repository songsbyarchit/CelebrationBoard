from app import db    #get db from init

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)    #basic model without security
    username = db.Column(db.String(80), unique=True, nullable=False)  #username must be unique
    email = db.Column(db.String(120), unique=True, nullable=False)    #email must be unique
    department = db.Column(db.String(50), nullable=False)    #required field
    job_title = db.Column(db.String(100), nullable=False)    #required field
    password = db.Column(db.String(120), nullable=False)    #still storing as plain text (bad)

    def __repr__(self):
        return f'<User {self.username}>'   #helps with debuging later