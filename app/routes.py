from flask import render_template, redirect, url_for, flash  #need these for templates
from app import app, db
from app.models import User

@app.route('/')
def home():
    return render_template('index.html')   #now using template instead of text

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')    #basic login without security yet

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')    #simple register no validation