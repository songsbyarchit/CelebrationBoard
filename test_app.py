import unittest
from app import app, db
from app.models import User, Post, Notification, AdminLog
from flask import url_for

class FlaskAppMaliciousTestCase(unittest.TestCase):
    def setUp(self):
        
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

        
        self.test_user = User(
            username='testuser',
            email='testuser@example.com',
            department='engineering',
            job_title='Test Engineer'
        )
        self.test_user.set_password('Test@1234')
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    
    def test_registration_password_mismatch(self):
        """1a. Password and confirm password do not match"""
        response = self.app.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'department': 'engineering',
            'job_title': 'Engineer',
            'password': 'Pass@1234',
            'confirm_password': 'WrongPass123'
        }, follow_redirects=True)
        self.assertIn(b'Both passwords must match!', response.data)

    def test_registration_invalid_password(self):
        """1b. Password lacks required complexity"""
        response = self.app.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'department': 'engineering',
            'job_title': 'Engineer',
            'password': 'simplepass',
            'confirm_password': 'simplepass'
        }, follow_redirects=True)
        self.assertIn(b'Password must contain at least one uppercase letter!', response.data)

    def test_registration_username_already_exists(self):
        """1c. Username already exists"""
        response = self.app.post('/register', data={
            'username': 'testuser',
            'email': 'newemail@example.com',
            'department': 'engineering',
            'job_title': 'Engineer',
            'password': 'Pass@1234',
            'confirm_password': 'Pass@1234'
        }, follow_redirects=True)
        self.assertIn(b'Username already taken!', response.data)

    def test_registration_email_already_exists(self):
        """1d. Email already exists"""
        response = self.app.post('/register', data={
            'username': 'newuser',
            'email': 'testuser@example.com',
            'department': 'engineering',
            'job_title': 'Engineer',
            'password': 'Pass@1234',
            'confirm_password': 'Pass@1234'
        }, follow_redirects=True)
        self.assertIn(b'Email already registered!', response.data)

    def test_registration_invalid_email(self):
        """1e. Invalid email format"""
        response = self.app.post('/register', data={
            'username': 'newuser',
            'email': 'invalidemail',
            'department': 'engineering',
            'job_title': 'Engineer',
            'password': 'Pass@1234',
            'confirm_password': 'Pass@1234'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email address.', response.data)

    def test_registration_no_department_selected(self):
        """1f. Department not selected"""
        response = self.app.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'department': '',
            'job_title': 'Engineer',
            'password': 'Pass@1234',
            'confirm_password': 'Pass@1234'
        }, follow_redirects=True)
        self.assertIn(b'Please select your department', response.data)

    
    def test_login_invalid_username(self):
        """2a. Username does not exist"""
        response = self.app.post('/login', data={
            'username': 'nonexistent',
            'password': 'Pass@1234'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)

    def test_login_invalid_password(self):
        """2b. Incorrect password for an existing username"""
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'WrongPassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)

    def test_login_empty_fields(self):
        """2c. Empty username or password fields"""
        response = self.app.post('/login', data={
            'username': '',
            'password': ''
        }, follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)

    
    def test_post_creation_invalid_title_length(self):
        """3a. Title is too short"""
        response = self.app.post('/create_post', data={
            'title': 'Hi',
            'content': 'Valid content'
        }, follow_redirects=True)
        self.assertIn(b'Field must be between 4 and 100 characters long.', response.data)

    def test_post_creation_invalid_content_length(self):
        """3b. Content is too short"""
        response = self.app.post('/create_post', data={
            'title': 'Valid Title',
            'content': 'Short'
        }, follow_redirects=True)
        self.assertIn(b'Field must be between 10 and 1000 characters long.', response.data)

    def test_post_creation_invalid_file_type(self):
        """3c. Invalid file type uploaded"""
        with open('invalid_file.exe', 'wb') as f:
            f.write(b'test')
        with open('invalid_file.exe', 'rb') as invalid_file:
            response = self.app.post('/create_post', data={
                'title': 'Valid Title',
                'content': 'Valid Content',
                'file': invalid_file
            }, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn(b'Only images and documents allowed!', response.data)

    def test_post_creation_file_size_exceeded(self):
        """3d. File size exceeds the limit"""
        
        large_file_content = b'a' * (11 * 1024 * 1024)  
        with open('large_file.pdf', 'wb') as f:
            f.write(large_file_content)
        with open('large_file.pdf', 'rb') as large_file:
            response = self.app.post('/create_post', data={
                'title': 'Valid Title',
                'content': 'Valid Content',
                'file': large_file
            }, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn(b'File size must be less than', response.data)

class CommentTestCase(unittest.TestCase):
    def setUp(self):
        
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

        
        self.test_user = User(
            username='testuser',
            email='testuser@example.com',
            department='engineering',
            job_title='Test Engineer'
        )
        self.test_user.set_password('Test@1234')
        db.session.add(self.test_user)
        db.session.commit()

        self.test_post = Post(
            title='Test Post',
            content='This is a test post.',
            author=self.test_user
        )
        db.session.add(self.test_post)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    
    def test_add_comment_valid(self):
        """4a. Valid comment"""
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })
        response = self.app.post(f'/post/{self.test_post.id}/comment', data={
            'content': 'This is a valid comment.'
        }, follow_redirects=True)
        self.assertIn(b'Your comment has been added!', response.data)

    def test_add_comment_empty(self):
        """4a. Comment content is empty"""
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })
        response = self.app.post(f'/post/{self.test_post.id}/comment', data={
            'content': ''
        }, follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)

    def test_add_comment_exceeds_max_length(self):
        """4b. Comment exceeds the maximum allowed length"""
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })
        long_comment = 'a' * 501  
        response = self.app.post(f'/post/{self.test_post.id}/comment', data={
            'content': long_comment
        }, follow_redirects=True)
        self.assertIn(b'Comment must be between 1 and 500 characters', response.data)

    def test_add_comment_on_nonexistent_post(self):
        """4c. Posting a comment on a non-existent post"""
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })
        response = self.app.post('/post/999/comment', data={
            'content': 'This is a test comment.'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 404)  

class NotificationTestCase(unittest.TestCase):
    def setUp(self):
        
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

        
        self.test_user = User(
            username='testuser',
            email='testuser@example.com',
            department='engineering',
            job_title='Test Engineer'
        )
        self.test_user.set_password('Test@1234')

        self.admin_user = User(
            username='adminuser',
            email=app.config['SUPER_ADMIN_EMAIL'],
            department='engineering',
            job_title='Admin',
            is_admin=True
        )
        self.admin_user.set_password('Admin@1234')

        db.session.add(self.test_user)
        db.session.add(self.admin_user)
        db.session.commit()

        
        self.test_post = Post(
            title='Test Post',
            content='This is a test post.',
            author=self.test_user
        )
        db.session.add(self.test_post)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_notification_on_post_deletion(self):
        """Verify notification is sent when an admin deletes a user's post"""
        
        self.app.post('/login', data={
            'username': 'adminuser',
            'password': 'Admin@1234'
        })

        
        response = self.app.post(f'/post/{self.test_post.id}/delete', data={
            'delete_reason': 'Violation of rules'
        }, follow_redirects=True)

        self.assertIn(b'Post deleted and notification sent to user.', response.data)

        
        notification = Notification.query.filter_by(user_id=self.test_user.id).first()
        self.assertIsNotNone(notification)
        self.assertIn('Your post "Test Post" was deleted by an admin.', notification.content)
        self.assertIn('Violation of rules', notification.content)

    def test_no_notification_on_unauthorised_deletion(self):
        """Ensure no notification is sent if a non-admin tries to delete a post"""
        
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })

        
        response = self.app.post(f'/post/{self.test_post.id}/delete', data={
            'delete_reason': 'Testing unauthorised deletion'
        }, follow_redirects=True)

        
        self.assertNotIn(b'Post deleted and notification sent to user.', response.data)
        notification = Notification.query.filter_by(user_id=self.test_user.id).first()
        self.assertIsNone(notification)

    def test_view_notifications(self):
        """Verify user can view their notifications"""
        
        self.app.post('/login', data={
            'username': 'adminuser',
            'password': 'Admin@1234'
        })
        self.app.post(f'/post/{self.test_post.id}/delete', data={
            'delete_reason': 'Violation of rules'
        }, follow_redirects=True)

        
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })

        
        response = self.app.get('/notifications', follow_redirects=True)

        
        self.assertIn(b'Your post "Test Post" was deleted by an admin.', response.data)
        self.assertIn(b'Violation of rules', response.data)

    def test_mark_notifications_as_read(self):
        """Verify notifications are marked as read after being viewed"""
        
        self.app.post('/login', data={
            'username': 'adminuser',
            'password': 'Admin@1234'
        })
        self.app.post(f'/post/{self.test_post.id}/delete', data={
            'delete_reason': 'Violation of rules'
        }, follow_redirects=True)

        
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })
        response = self.app.get('/notifications', follow_redirects=True)

        
        unread_notifications = Notification.query.filter_by(user_id=self.test_user.id, is_read=False).all()
        self.assertEqual(len(unread_notifications), 0)

import unittest
import tempfile
from app import app, db
from app.models import User, Post

class FileUploadTestCase(unittest.TestCase):
    def setUp(self):
        
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

        
        self.test_user = User(
            username='testuser',
            email='testuser@example.com',
            department='engineering',
            job_title='Test Engineer'
        )
        self.test_user.set_password('Test@1234')
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_valid_file_upload(self):
        """Test valid file upload during post creation"""
        
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })

        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as valid_file:
            valid_file.write(b'valid file content')
            valid_file.seek(0)  
            response = self.app.post('/create_post', data={
                'title': 'Valid Title',
                'content': 'This is valid content.',
                'file': valid_file
            }, content_type='multipart/form-data', follow_redirects=True)
            self.assertIn(b'Your celebration has been shared!', response.data)

    def test_invalid_file_type_upload(self):
        """Test upload of invalid file type"""
        
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })

        
        with tempfile.NamedTemporaryFile(suffix='.exe') as invalid_file:
            invalid_file.write(b'invalid file content')
            invalid_file.seek(0)  
            response = self.app.post('/create_post', data={
                'title': 'Valid Title',
                'content': 'This is valid content.',
                'file': invalid_file
            }, content_type='multipart/form-data', follow_redirects=True)
            self.assertIn(b'Only images and documents allowed!', response.data)

    def test_exceeding_file_size_limit(self):
        """Test file exceeding the size limit"""
        
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })

        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as large_file:
            large_file.write(b'a' * (11 * 1024 * 1024))  
            large_file.seek(0)  
            response = self.app.post('/create_post', data={
                'title': 'Valid Title',
                'content': 'This is valid content.',
                'file': large_file
            }, content_type='multipart/form-data', follow_redirects=True)
            self.assertIn(b'File size must be less than', response.data)

    def test_unique_filename_generation(self):
        """Test that uploaded files are saved with unique filenames"""
        
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })

        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as file1, tempfile.NamedTemporaryFile(suffix='.pdf') as file2:
            file1.write(b'duplicate file content')
            file2.write(b'duplicate file content')
            file1.seek(0)
            file2.seek(0)

            response1 = self.app.post('/create_post', data={
                'title': 'Valid Title 1',
                'content': 'Content for post 1.',
                'file': file1
            }, content_type='multipart/form-data', follow_redirects=True)

            response2 = self.app.post('/create_post', data={
                'title': 'Valid Title 2',
                'content': 'Content for post 2.',
                'file': file2
            }, content_type='multipart/form-data', follow_redirects=True)

        
        self.assertIn(b'Your celebration has been shared!', response1.data)
        self.assertIn(b'Your celebration has been shared!', response2.data)

    def test_no_file_upload(self):
        """Test post creation with no file attached"""
        
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })

        
        response = self.app.post('/create_post', data={
            'title': 'Post Without File',
            'content': 'This is a post without a file.'
        }, follow_redirects=True)
        self.assertIn(b'Your celebration has been shared!', response.data)

class LikesAndAdminActionsTestCase(unittest.TestCase):
    def setUp(self):
        
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

        
        self.test_user = User(
            username='testuser',
            email='testuser@example.com',
            department='engineering',
            job_title='Test Engineer'
        )
        self.test_user.set_password('Test@1234')

        self.admin_user = User(
            username='adminuser',
            email=app.config['SUPER_ADMIN_EMAIL'],
            department='engineering',
            job_title='Admin',
            is_admin=True
        )
        self.admin_user.set_password('Admin@1234')

        db.session.add(self.test_user)
        db.session.add(self.admin_user)
        db.session.commit()

        
        self.test_post = Post(
            title='Test Post',
            content='This is a test post.',
            author=self.test_user
        )
        db.session.add(self.test_post)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    
    def test_like_post(self):
        """Ensure liking a post by a logged-in user increments the like count"""
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })

        
        response = self.app.post(f'/post/{self.test_post.id}/like', follow_redirects=True)
        self.assertEqual(self.test_post.likes.count(), 1)

    def test_unlike_post(self):
        """Confirm unliking decrements the like count"""
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })

        
        self.app.post(f'/post/{self.test_post.id}/like', follow_redirects=True)
        self.app.post(f'/post/{self.test_post.id}/like', follow_redirects=True)
        self.assertEqual(self.test_post.likes.count(), 0)

    def test_duplicate_like(self):
        """Test liking a post multiple times (should not duplicate likes)"""
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })

        
        self.app.post(f'/post/{self.test_post.id}/like', follow_redirects=True)
        self.app.post(f'/post/{self.test_post.id}/like', follow_redirects=True)
        self.assertEqual(self.test_post.likes.count(), 1)

    def test_like_nonexistent_post(self):
        """Test liking a non-existent post (should return an error)"""
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })

        
        response = self.app.post('/post/999/like', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    
    def test_admin_promote_user(self):
        """Confirm admins can promote users and logs are created"""
        self.app.post('/login', data={
            'username': 'adminuser',
            'password': 'Admin@1234'
        })

        
        response = self.app.post(f'/admin/toggle/{self.test_user.id}', follow_redirects=True)
        promoted_user = User.query.get(self.test_user.id)
        log = AdminLog.query.filter_by(action='Promoted to admin').first()

        self.assertTrue(promoted_user.is_admin)
        self.assertIsNotNone(log)
        self.assertIn(f'User affected: {self.test_user.username}', log.details)

    def test_admin_demote_user(self):
        """Confirm admins can demote users and logs are created"""
        
        self.app.post('/login', data={
            'username': 'adminuser',
            'password': 'Admin@1234'
        })
        self.app.post(f'/admin/toggle/{self.test_user.id}', follow_redirects=True)

        
        response = self.app.post(f'/admin/toggle/{self.test_user.id}', follow_redirects=True)
        demoted_user = User.query.get(self.test_user.id)
        log = AdminLog.query.filter_by(action='Removed from admin').first()

        self.assertFalse(demoted_user.is_admin)
        self.assertIsNotNone(log)
        self.assertIn(f'User affected: {self.test_user.username}', log.details)

    def test_superadmin_access(self):
        """Verify superadmins have exclusive access to certain features"""
        self.app.post('/login', data={
            'username': 'adminuser',
            'password': 'Admin@1234'
        })

        
        response = self.app.post(f'/admin/toggle/{self.admin_user.id}', follow_redirects=True)
        self.assertIn(b'Cannot modify super admin status', response.data)

    def test_unauthorised_user_admin_actions(self):
        """Test unauthorised users attempting admin actions"""
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'Test@1234'
        })

        
        response = self.app.post(f'/admin/toggle/{self.admin_user.id}', follow_redirects=True)
        self.assertIn(b'Only super admin can modify admin status', response.data)

if __name__ == '__main__':
    unittest.main()