from app import db
from werkzeug.security import generate_password_hash, check_password_hash    #for password hashing
from flask_login import UserMixin    #add login functionality to User model
from datetime import datetime

#db model defining a user
class User(db.Model, UserMixin):    #inherit from UserMixin for login support
    id = db.Column(db.Integer, primary_key=True)    #basic model w/o security for now
    username = db.Column(db.String(80), unique=True, nullable=False)  #username must be unique
    email = db.Column(db.String(120), unique=True, nullable=False)    #email must be unique
    department = db.Column(db.String(50), nullable=False)    #required field
    job_title = db.Column(db.String(100), nullable=False)    # required field
    password_hash = db.Column(db.String(256), nullable=False)    #  store only hashed passwords, never plain text
    posts = db.relationship('Post', backref='author', lazy=True)    #link to user's posts
    comments = db.relationship('Comment', backref='author', lazy=True)    #link to user's comments
    is_admin = db.Column(db.Boolean, default=False)    # false by default
    promoted_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)    # Fixed syntax here
    admin_action_logs = db.relationship('AdminLog', backref='admin', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True,
                                  order_by="desc(Notification.timestamp)")
    likes = db.relationship('Like', backref='user', lazy=True)
    
    def set_password(self, password):    #method to hash password before storing
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):    #method to verify password via hash
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

#db model defining what's tracked/stored in the admin log
class AdminLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)

    def __repr__(self):
        return f'<AdminLog action={self.action} admin_id={self.admin_id}>'

#db model defining a post
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)    #unique id for each post
    title = db.Column(db.String(100), nullable=False)    #celebration title/headline
    content = db.Column(db.Text, nullable=False)    #celebration description
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)    #when it was posted
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)    #who posted it
    file_filename = db.Column(db.String(255))    #store filename of uploaded file
    file_path = db.Column(db.String(255))    #store path to uploaded file
    comments = db.relationship('Comment', backref='post', lazy=True, 
                             cascade='all, delete-orphan')    #link to comments
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Post {self.title}>'

#db model defining a comment
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f'<Comment {self.content[:20]}...>'

#db model defining the things tracked when a post is deleted
class PostDeletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(100))  # Store post title for reference
    deleted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.Text, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Original post owner
    admin = db.relationship('User', foreign_keys=[admin_id])
    user = db.relationship('User', foreign_keys=[user_id])

#db model defining a "notification"
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    notification_type = db.Column(db.String(50), nullable=False, default='generic')

#db model defining a "like"
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)