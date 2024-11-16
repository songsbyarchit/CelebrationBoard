import os
from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.models import User, Post
from app.forms import LoginForm, RegistrationForm    #import our new forms
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime

@app.route('/')
@login_required    #protect the home page

def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()    #get all posts, newest first
    return render_template('index.html', posts=posts)    #pass posts to template

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

from app.forms import PostForm    # Add this at the top with your other imports

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        file_path = None
        file_filename = None
        
        if form.file.data:
            file = form.file.data
            # Secure the filename
            filename = secure_filename(file.filename)
            # Create unique filename
            file_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
            # Make sure upload folder exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            # Save file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_filename))

        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
            file_filename=file_filename,
            file_path=f"uploads/{file_filename}" if file_filename else None
        )
        db.session.add(post)
        db.session.commit()
        flash('Your celebration has been shared!')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)