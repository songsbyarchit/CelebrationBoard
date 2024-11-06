# Employee Celebration Board

An application (built using flask) for recognising employee achievements. This tool is designed to boost workplace morale and create a positive, inclusive environment.

## Current Features

The application provides secure user-authentication. Users can register using their work credentials. The system incorporates role-based access management. All passwords undergo secure hashing before storage.

### Security Features(sofar)

- Password hashing through Werkzeug
- Session management using Flask-Login 
- Form protection utilising WTForms with CSRF
- Deailedorm validations
- Protected application routes

### User Registration Systm

The registration process captures several details:
- Unique username (4-20 characters)
- Corporate email addres
- Selection of department
- Current job title
- Password meeting securiry requirments

### Password Requirements

Each password must fulfil these criteria:
- Contains 8 or more characters
- Includes at least one uppercase letter
- Contains at least one numbr
- Includes at least one special character
- Must not contain the username