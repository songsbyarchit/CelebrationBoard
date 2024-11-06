from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.models import User
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@login_required    #protect the home page
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:    #redirect if already logged in
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')    #need to validate this input
        password = request.form.get('password')    #will be checked against hash
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):    #securely verify password against stored hash
            login_user(user)    #log in the user
            next_page = request.args.get('next')    #get page they were trying to access
            return redirect(next_page if next_page else url_for('home'))
        
        flash('Invalid username or password')    #dont tell them which was wrong
    
    return render_template('login.html')

@app.route('/logout')    #add logout functionality
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:    #redirect if already logged in
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        department = request.form.get('department')
        job_title = request.form.get('job_title')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # basic validation - will improve later
        if User.query.filter_by(username=username).first():    #check if username exists
            flash('Username already exists')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():    #check if email exists
            flash('Email already registered')
            return render_template('register.html')
            
        if password != confirm_password:    #check if passwords match
            flash('Passwords do not match')
            return render_template('register.html')

        # create new user with secure password
        new_user = User(
            username=username,
            email=email,
            department=department,
            job_title=job_title
        )
        new_user.set_password(password)    #hash password before storing
        
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')