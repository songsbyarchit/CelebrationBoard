from app import db    #get db from init instead of creating it here

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)    #basic model without security
    username = db.Column(db.String(80), unique=True, nullable=False)  #simple username field for now
    password = db.Column(db.String(120), nullable=False)  #storing passwords in plain text (make it with more security Later!)

    def __repr__(self):
        return f'<User {self.username}>'   #helps with debuging later