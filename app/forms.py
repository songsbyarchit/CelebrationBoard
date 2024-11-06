from flask_wtf import FlaskForm    #secure form handling
from wtforms import StringField, PasswordField, SelectField, SubmitField    #form fields
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp    #validators
from app.models import User    #for custom validation

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