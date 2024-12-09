from flask import render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
from app import app, db
from app.models import User, Post, Notification, Comment, Like, AdminLog
from app.forms import LoginForm, RegistrationForm, PostForm, CommentForm, FilterForm
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import os
import uuid

@app.route('/', methods=['GET'])
@login_required
def home():
    form = CommentForm()
    filter_form = FilterForm(request.args)
    
    query = Post.query
    
    # department filter
    if filter_form.department.data and filter_form.department.data != '':
        query = query.join(User).filter(User.department == filter_form.department.data)
    
    # search filter
    if filter_form.search.data:
        search_term = filter_form.search.data.strip()
        if len(search_term) > 50:
            flash('Search query too long.', 'error')
            return redirect(url_for('home'))
        search = f"%{search_term}%"
        query = query.filter((Post.title.ilike(search)) | (Post.content.ilike(search)))
    
    # apply sorting of posts
    sort_by = filter_form.sort_by.data or 'date_desc'  # default to newest first
    if sort_by == 'date_desc':
        query = query.order_by(Post.date_posted.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(Post.date_posted.asc())
    elif sort_by == 'likes':
        query = query.outerjoin(Like)\
                    .group_by(Post.id)\
                    .order_by(db.func.count(Like.id).desc(), Post.date_posted.desc())
    else:
        query = query.order_by(Post.date_posted.desc())
    
    posts = query.all()
    return render_template('index.html', posts=posts, form=form, filter_form=filter_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:    #redirect if already logged in
        return redirect(url_for('home'))
        
    form = LoginForm()    #create form instance
    if form.validate_on_submit():    #handles POST request and validation
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):    #securely verify password vs stored hash
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
        # Check if email matches SUPER_ADMIN_EMAIL from .env
        is_admin = form.email.data == app.config['SUPER_ADMIN_EMAIL']
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            department=form.department.data,
            job_title=form.job_title.data,
            is_admin=is_admin  # Set admin status based on superadmin email
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        file_path = None
        file_filename = None
        
        if form.file.data:
            file = form.file.data
            # Validate the file type
            if not allowed_file(file.filename):
                flash('Invalid file type. Only the following types are allowed: png, jpg, jpeg, gif, pdf, doc, docx.')
                return redirect(request.url)

            # generate secure, unique filename
            unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            # ensure the upload folder still exists!
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            # save upoaded file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            
            # update file path & filename for the database
            file_filename = unique_filename
            file_path = f"uploads/{unique_filename}"

        # ceate post object
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
            file_filename=file_filename,
            file_path=file_path
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
            #  new file upload handling
            file = form.file.data
            filename = secure_filename(file.filename)
            file_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_filename))
            post.file_filename = file_filename
            post.file_path = f"uploads/{file_filename}"
            
        db.session.commit()
        flash('Your post has been updated!')
        return redirect(url_for('home'))
    
    # prepopulate form with data from pre-edit
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
            # create notif to be sent to person who wrote post
            notification = Notification(
                user_id=post.author.id,
                content=f'An admin deleted your post "{post.title}". Reason: {reason}',
                notification_type='post_deletion'
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
        
        # add notif for post author but not if user is himself the author of the post (only notify if the user is not the post author)
        if post.author != current_user:
            notification = Notification(
                user_id=post.author.id,
                content=f"{current_user.username} commented on your post: \"{post.title}\"",
                notification_type='comment',
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
        
        flash('Your comment has been added!')
    
    return redirect(url_for('home'))

@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if like:
        db.session.delete(like)
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
    
    db.session.commit()

    # add notif to be sent to post author but not if the user liked their own post (only notify if like is from someone else)
    if like and post.author != current_user:
        notification = Notification(
            user_id=post.author.id,
            content=f"{current_user.username} liked your post: \"{post.title}\"",
            notification_type='like',  # specify notif type to keep variables up to date for when sent later
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()

    return redirect(url_for('home'))

@app.route('/notifications')
@login_required
def notifications():
    # get ALL notifications (read and unread)
    notifications = Notification.query.filter_by(user_id=current_user.id)\
                                   .order_by(Notification.timestamp.desc())\
                                   .all()
    # mark unread ones as read since the page has been clicked on
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
    return render_template('admin_manage.html', users=users, super_admin_email=os.environ.get('SUPER_ADMIN_EMAIL'))

@app.route('/admin/toggle/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    try:
        if current_user.email != os.environ.get('SUPER_ADMIN_EMAIL'):
            flash('Only super admin can modify admin status')
            return redirect(url_for('home'))

        user = User.query.get_or_404(user_id)

        if user.email == os.environ.get('SUPER_ADMIN_EMAIL'):
            flash('Cannot modify super admin status')
            return redirect(url_for('admin_manage'))

        was_admin = user.is_admin
        user.is_admin = not user.is_admin
        user.promoted_by_id = current_user.id if user.is_admin else None

        log = AdminLog(
            admin_id=current_user.id,
            action=f"{'Promoted to' if user.is_admin else 'Removed from'} admin",
            details=f"User affected: {user.username}"
        )
        db.session.add(log)

        if user.is_admin and not was_admin:
            notification = Notification(
                user_id=user.id,
                content=f"You have been promoted to admin by {current_user.username}",
                is_read=False
            )
            db.session.add(notification)
        elif not user.is_admin and was_admin:
            notification = Notification(
                user_id=user.id,
                content=f"You have been removed from admin by {current_user.username}",
                is_read=False
            )
            db.session.add(notification)

        db.session.commit()

        flash(f"User {user.username} {'promoted to' if user.is_admin else 'removed from'} admin role")
        return redirect(url_for('admin_manage'))

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('admin_manage'))