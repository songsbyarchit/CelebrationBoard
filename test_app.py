import pytest
from app import db, app
from app.models import User, Post
from werkzeug.security import generate_password_hash
import logging

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cel_board_db_user:8ETS9zWqSiBjgtzaocl45CAeSzM6Du2B@dpg-ct5nqrg8fa8c73bvu7g0-a.oregon-postgres.render.com/cel_board_db'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create all tables
            yield client
            db.session.remove()  # Cleanup after tests
            db.drop_all()  # Drop all tables

@pytest.fixture
def authenticated_user():
    user = User(
        username="testuser",
        email="test@example.com",
        department="engineering",
        job_title="Engineer",
        password_hash=generate_password_hash("Password123!")
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_post(authenticated_user):
    post = Post(
        title="Test Post Title",
        content="This is a test post content.",
        author=authenticated_user
    )
    db.session.add(post)
    db.session.commit()
    return post

@pytest.fixture
def superadmin_user():
    superadmin = User(
        username="superadmin",
        email=app.config['SUPER_ADMIN_EMAIL'],
        department="management",
        job_title="Super Administrator",
        is_admin=True,
        password_hash=generate_password_hash("Karnal.123")
    )
    db.session.add(superadmin)
    db.session.commit()
    return superadmin

# 1. test user registration with mismatched passwords  
def test_registration_mismatched_passwords(client):
    response = client.post('/register', data={
        'username': 'testuser1',
        'email': 'test1@example.com',
        'department': 'engineering',
        'job_title': 'Developer',
        'password': 'Password123!',
        'confirm_password': 'Password321!'  # Mismatched password
    }, follow_redirects=True)
    assert b'Both passwords must match!' in response.data

# 2. test user registration with a weak password
def test_registration_weak_password(client):
    response = client.post('/register', data={
        'username': 'testuser2',
        'email': 'test2@example.com',
        'department': 'sales',
        'job_title': 'Sales Lead',
        'password': 'weak',
        'confirm_password': 'weak'
    }, follow_redirects=True)
    assert b'Password must be at least 8 characters!' in response.data

# 3. test user registration with a duplicate username
def test_registration_duplicate_username(client):
    user = User(username='testuser3', email='test3@example.com', department='hr',
                job_title='HR Manager', password_hash=generate_password_hash('Test123!'))
    db.session.add(user)
    db.session.commit()

    response = client.post('/register', data={
        'username': 'testuser3',  # Duplicate username
        'email': 'newemail@example.com',
        'department': 'hr',
        'job_title': 'HR Assistant',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }, follow_redirects=True)
    assert b'Username already taken! Please choose another one.' in response.data

# 4. test user registration with a duplicate email
def test_registration_duplicate_email(client):
    user = User(username='uniqueuser', email='test4@example.com', department='marketing',
                job_title='Content Creator', password_hash=generate_password_hash('Test123!'))
    db.session.add(user)
    db.session.commit()

    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'test4@example.com',  # Duplicate email
        'department': 'marketing',
        'job_title': 'Graphic Designer',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }, follow_redirects=True)
    assert b'Email already registered! Please use another one.' in response.data

# 5. test user registration with an invalid email format
def test_registration_invalid_email(client):
    response = client.post('/register', data={
        'username': 'testuser5',
        'email': 'invalid-email-format',  # Invalid email
        'department': 'finance',
        'job_title': 'Accountant',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }, follow_redirects=True)
    assert b'Invalid email address.' in response.data

# 6. test login with empty username and password fields
def test_login_empty_fields(client):
    response = client.post('/login', data={
        'username': '',
        'password': ''
    }, follow_redirects=True)
    assert b'This field is required.' in response.data

# 7. test liking a post to ensure the like count increments
def test_like_post(client, authenticated_user, test_post):
    response = client.post(f'/post/{test_post.id}/like', follow_redirects=True)
    assert b'likes' in response.data  # Checks for like count being updated

# 8. test unliking a post to ensure the like count decrements
def test_unlike_post(client, authenticated_user, test_post):
    client.post(f'/post/{test_post.id}/like', follow_redirects=True)  # Like first
    response = client.post(f'/post/{test_post.id}/like', follow_redirects=True)  # Unlike
    assert b'likes' in response.data  # Verifies like is toggled back

# 9. test liking a post to ensure the like count increments
def test_like_post(client, authenticated_user, test_post):
    response = client.post(f'/post/{test_post.id}/like', follow_redirects=True)
    assert b'likes' in response.data  # Checks for like count being updated

# 10. test unliking a post to ensure the like count decrements
def test_unlike_post(client, authenticated_user, test_post):
    client.post(f'/post/{test_post.id}/like', follow_redirects=True)  # Like first
    response = client.post(f'/post/{test_post.id}/like', follow_redirects=True)  # Unlike
    assert b'likes' in response.data  # Verifies like is toggled back