from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.models import User
from app.forms import LoginForm, RegistrationForm    #import our new forms
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@login_required    #protect the home page
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:    #redirect if already logged in
        return redirect(url_for('home'))
        
    form = LoginForm()    #create form instance
    if form.validate_on_submit():    #handles POST request and validation
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):    #securely verify password against stored hash
            login_user(user)    #log in the user
            flash('Successfully logged in!')    # Add success message
            next_page = request.args.get('next')    #get page they were trying to access
            return redirect(next_page if next_page else url_for('home'))
        else:
            flash('Invalid username or password')    #dont tell them which was wrong
            return render_template('login.html', form=form)    # Return to form with data
    
    if form.errors:    # Add validation error messages
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}')
    
    return render_template('login.html', form=form)    #pass form to template

@app.route('/logout')    #add logout functionality
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:    #redirect if already logged in
        return redirect(url_for('home'))
        
    form = RegistrationForm()    #create form instance
    if form.validate_on_submit():    #handles POST request and validation
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            department=form.department.data,
            job_title=form.job_title.data
        )
        new_user.set_password(form.password.data)    #hash password before storing
        
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)    #pass form to template