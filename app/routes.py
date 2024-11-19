from flask import render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
from app import app, db
from app.models import User, Post, Notification, Comment, Like
from app.forms import LoginForm, RegistrationForm, PostForm, CommentForm, FilterForm
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import os

@app.route('/', methods=['GET'])
@login_required
def home():
    form = CommentForm()
    filter_form = FilterForm(request.args)  # Initialize with request args to preserve selections
    
    # Get base query
    query = Post.query
    
    # Apply department filter
    if filter_form.department.data and filter_form.department.data != '':
        query = query.join(User).filter(User.department == filter_form.department.data)
    
    # Apply search filter
    if filter_form.search.data:
        search = f"%{filter_form.search.data}%"
        query = query.filter((Post.title.like(search)) | (Post.content.like(search)))
    
    # Apply sorting
    sort_by = filter_form.sort_by.data or 'date_desc'  # Default to newest first
    if sort_by == 'date_desc':
        query = query.order_by(Post.date_posted.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(Post.date_posted.asc())
    elif sort_by == 'likes':
        query = query.outerjoin(Like)\
                    .group_by(Post.id)\
                    .order_by(db.func.count(Like.id).desc(), Post.date_posted.desc())
    elif sort_by == 'comments':
        query = query.outerjoin(Comment)\
                    .group_by(Post.id)\
                    .order_by(db.func.count(Comment.id).desc(), Post.date_posted.desc())
    else:
        query = query.order_by(Post.date_posted.desc())
    
    posts = query.all()
    return render_template('index.html', 
                         posts=posts, 
                         form=form, 
                         filter_form=filter_form)

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

@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if like:
        # Unlike if already liked
        db.session.delete(like)
    else:
        # Add new like
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
    
    db.session.commit()
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

@app.route('/admin/manage', methods=['GET'])
@login_required
def admin_manage():
    if not current_user.is_admin and current_user.email != os.environ.get('SUPER_ADMIN_EMAIL'):
        flash('Access denied')
        return redirect(url_for('home'))
    
    users = User.query.all()
    return render_template('admin_manage.html', users=users)

@app.route('/admin/toggle/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if current_user.email != os.environ.get('SUPER_ADMIN_EMAIL'):
        flash('Only super admin can modify admin status')
        return redirect(url_for('home'))
    
    user = User.query.get_or_404(user_id)
    if user.email == os.environ.get('SUPER_ADMIN_EMAIL'):
        flash('Cannot modify super admin status')
        return redirect(url_for('admin_manage'))
    
    user.is_admin = not user.is_admin
    user.promoted_by_id = current_user.id if user.is_admin else None
    
    log = AdminLog(
        admin_id=current_user.id,
        action=f"{'Promoted to' if user.is_admin else 'Removed from'} admin",
        details=f"User affected: {user.username}"
    )
    
    db.session.add(log)
    db.session.commit()
    
    flash(f"User {user.username} {'promoted to' if user.is_admin else 'removed from'} admin role")
    return redirect(url_for('admin_manage'))