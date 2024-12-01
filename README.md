# Employee celebration Board

## ADMIN LOGIN

Admin user is already spun up and added to database.

His username/password are stored in .env but here they are for ease of use. in production, obviously they
wouldn't be shared here!

- Username: admin
- Password: Karnal.123

## Built using + Purpose

An application built using Flask. It recognises employee achievements. The tool creates a positive and inclusive workplace. It helps boost morale through shared accomplishments.

## Current features

- The application includes secure user authentication.
- Users register with their work credentials.
- The system uses role-based access management.
- Passwords are securely hashed before storage.
- Notifications are sent to users when their posts are deleted by an admin.

### Security Features

- Password hashing is implemented using Werkzeug.
- Sessions are managed securely through Flask-Login.
- Forms are protected with WTForms and CSRF.
- Input validation is thorough.
- Routes are restricted to authorised users.

### User registration system

- The registration process requires several details:
  - Unique username (4-20 characters long).
  - Corporate email address.
  - Department selection.
  - Current job title.
  - Passwords meeting security standards.

### Password Requirements

- Each password must meet specific criteria:
  - Must have at least eight characters.
  - At least one letter must be uppercase.
  - Must include a number.
  - At least one special character is required.
  - The username cannot appear in the password.

## Installation

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/songsbyarchit/CelebrationBoard.git