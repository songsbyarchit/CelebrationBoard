from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.models import User

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')    #need to validate this input
        password = request.form.get('password')    #need to hash this later
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:    #never compare passwords directly like this
            flash('Logged in successfully!')
            return redirect(url_for('home'))
        
        flash('Invalid username or password')    #dont tell them which was wrong
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
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

        # create new user - very insecure still
        new_user = User(
            username=username,
            email=email,
            department=department,
            job_title=job_title,
            password=password    #storing password as plain text (bad!)
        )
        
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')