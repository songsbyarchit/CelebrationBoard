from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.models import User

@app.route('/')
def home():
    return render_template('index.html')    #using template instead of text now

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')    #need to validate this input
        password = request.form.get('password')    #need to hash this later
        
        # basic check for now - very insecure!
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:    #never compare passwords directly like this
            flash('Logged in successfully!')
            return redirect(url_for('home'))
        
        flash('Invalid username or password')    #dont tell them which was wrong
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])    #add register route
def register():
    return render_template('register.html')    #just render template for now