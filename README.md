# Employee celebration Board

## ADMIN LOGIN

Super admin user is already spun up and added to database.

His username/password are stored in .env but here they are for ease of use. in production, obviously they
wouldn't be shared here!

- Username: admin
- Password: -----

## Built using + Purpose

This app was build using using Flask. It recognises employee achievementto help boost morale within Cisco by sharing accomplishments.

## Current features

- The application has secure user authentication (for login/register)
- Users can register with their work credentials
- The system has role-based access (user, admins and superadmins)
- Passwords are securely hashed (using SHA256) before storing them
- Notifications are sent to users when their posts are deleted by an admin, stating the reason of post deletion

### Security Features

- Password hashing uses Werkzeug
- Flask-Login is used to effectively manage sessions
- Forms are protected using WTForms and CSRF
- Inputs are thoroughly validated to ensure no SQL injections
- Routes are restricted to authorised users (using @login_required decorators etc)

### User registration system

- The registration process requires:
  - a Unique username (4-20 characters long)
  - a valid email address
  - Department selection (from dropdown menu)
  - Current job title
  - Passwords meeting security standards (8 characters, at least one lowercase, at least one uppercase, at least one special character)

  ### Render Integration

- Render hosts the PostgreSQL database, ensuring secure and reliable data storage  
- Database credentials are securely stored using environment variables  
- Deployments are automated through Render’s integration with GitHub  
- Builds are triggered directly from GitHub commits  
- Application logs and errors are monitored through Render's in-built dashboard  

## Installation

1. Clone the repo to your local machine if you would like to run/help with the building of it there!
   ```bash
   git clone https://github.com/songsbyarchit/CelebrationBoard.git

## SSH key

My SSH key is linked and I'm adding this info simply to make a commit to see if all works well!
