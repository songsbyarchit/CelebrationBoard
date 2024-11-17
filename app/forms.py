from flask_wtf import FlaskForm    #secure form handling
from flask_wtf.file import FileField, FileAllowed 
from wtforms import StringField, PasswordField, SelectField, SubmitField    #form fields
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp    #validators
from app.models import User    #for custom validation
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField
from wtforms.validators import ValidationError

class FileSize(object):
    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, form, field):
        if field.data:
            file_size = len(field.data.read()) / 1024 / 1024  # size in MB
            field.data.seek(0)  # Reset file pointer
            if file_size > self.max_size:
                raise ValidationError(f'File size must be less than {self.max_size}MB')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])    #required field
    password = PasswordField('Password', validators=[DataRequired()])    #required field
    submit = SubmitField('Login')    #submit button

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                         validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email',
                       validators=[DataRequired(), Email()])    #must be valid email
    department = SelectField('Department', 
                        choices=[
                            ('', '--- Select Department ---'),  # Blank default option
                            ('engineering', 'Engineering'),
                            ('sales', 'Sales'),
                            ('marketing', 'Marketing'),
                            ('hr', 'HR'),
                            ('finance', 'Finance')
                        ],
                        validators=[
                            DataRequired(message='Please select your department')
                        ],
                        default='',    # Set blank as default
                        coerce=str)    # Ensure proper string handling
    job_title = StringField('Job Title', 
                          validators=[DataRequired(), Length(max=100)])    #job title length limit
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters! '),
        Regexp(r'.*[A-Z]', message=' Password must contain at least one uppercase letter! '),
        Regexp(r'.*[0-9]', message=' Password must contain at least one number! '),
        Regexp(r'.*[!@#$%^&*(),.?":{}|<>]', message='Password must contain at least one special character! ')
    ])
    confirm_password = PasswordField('Confirm Password', 
                               validators=[
                                   DataRequired(), 
                                   EqualTo('password', message='Both passwords must match!')
                               ])

    def validate_username(self, username):    #custom validation for unique username
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken! Please choose another one.')

    def validate_password(self, password):    #custom password validation
        if self.username.data.lower() in password.data.lower():
            raise ValidationError('Password cannot contain username')

    def validate_email(self, email):    #custom validation for unique email
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered! Please use another one.')
        
class PostForm(FlaskForm):
    title = StringField('Title', 
                       validators=[
                           DataRequired(),
                           Length(min=4, max=100)
                       ])
    content = TextAreaField('Content', 
                          validators=[
                              DataRequired(),
                              Length(min=10, max=1000)
                          ])
    file = FileField('Attach File',
                    validators=[
                        FileAllowed(['jpg', 'png', 'gif', 'pdf', 'doc', 'docx'], 
                                  'Only images and documents allowed!'),
                        # Add a custom validator for file size
                        FileSize(max_size=10) # size in MB
                    ])
    
    submit = SubmitField('Share Celebration')