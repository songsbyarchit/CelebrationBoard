from flask import render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
from app import app, db
from app.models import User, Post, Notification, Comment
from app.forms import LoginForm, RegistrationForm, PostForm, CommentForm
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import os

@app.route('/')
@login_required    #protect the home page
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()    #get all posts, newest first
    form = CommentForm()    # Create instance of comment form
    return render_template('index.html', posts=posts, form=form)    #pass form to template

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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            department=form.department.data,
            job_title=form.job_title.data,
            is_admin=form.email.data.endswith('@admin.com')  # Make users with @admin.com email admins
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

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

@app.route("/post/<int:post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You can only edit your own posts!')
        return redirect(url_for('home'))
    
    form = PostForm()
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        
        if form.file.data:
            # Handle new file upload
            file = form.file.data
            filename = secure_filename(file.filename)
            file_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_filename))
            post.file_filename = file_filename
            post.file_path = f"uploads/{file_filename}"
            
        db.session.commit()
        flash('Your post has been updated!')
        return redirect(url_for('home'))
    
    # Pre-populate form with existing data
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    
    return render_template('create_post.html', 
                         title='Edit Post', 
                         form=form, 
                         legend='Edit Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.is_admin or post.author == current_user:
        reason = request.form.get('delete_reason')
        if current_user.is_admin and current_user != post.author:
            # Create notification for the post owner
            notification = Notification(
                user_id=post.author.id,
                content=f'Your post "{post.title}" was deleted by an admin. Reason: {reason}'
            )
            db.session.add(notification)
            flash(f'Post deleted and notification sent to user.')
        
        db.session.delete(post)
        db.session.commit()
        
    return redirect(url_for('home'))

@app.route("/post/<int:post_id>/comment", methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            post_id=post_id,
            author=current_user
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!')
    return redirect(url_for('home'))

@app.route('/notifications')
@login_required
def notifications():
    # Get all notifications, both read and unread
    notifications = Notification.query.filter_by(user_id=current_user.id)\
                                   .order_by(Notification.timestamp.desc())\
                                   .all()
    # Mark unread ones as read
    unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    for notification in unread:
        notification.is_read = True
    db.session.commit()
    return render_template('notifications.html', notifications=notifications)