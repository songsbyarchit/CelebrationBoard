from flask import Flask  
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)   #maek the app

app.config['SECRET_KEY'] = 'dev'    #dont use this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'   #basic database setup

db = SQLAlchemy(app)    #create the database

from app import routes  #get the routes
from app import models  #get the database models