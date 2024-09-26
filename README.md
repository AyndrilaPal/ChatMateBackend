# ChatMateBackend
It's a python based application
ChatMate is a Django-based web application that allows users to send interest messages to each other, manage their chat interactions, and maintain a user profile. 
## Features
- User registration and authentication
- Interest messaging system
- Real-time chat functionality
- User profiles with customizable settings
 ## Technologies Used

- **Backend**: Django, Django Channels,Daphne
- **Database**: PostgreSQL 
- **WebSocket**: Channels for real-time communication
- **Redis**: For caching and message brokering
- **JWT**: For secure user authentication

## Installation

1. *Clone the repository:*
   ```bash
   git clone https://github.com/AyndrilaPal/ChatMateBackend.git
   cd ChatMate
2. Set up a virtual environment:
    python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
3. Install dependencies:
   pip install -r requirements.txt
4. Set up the database:
   python3 manage.py makemigrations
   python3 manage.py migrate
6. Create a superuser (optional):
   python3 manage.py createsuperuser
7. Run the development server:
   python3 manage.py runserver
Configuration
  Update environment variables in .env or directly in your settings file, including:
  SECRET_KEY
  Database connection details
  Redis configuration
  JWT settings
Usage
  Navigate to http://127.0.0.1:8000 in your browser.
  Register a new account or log in as an existing user.
  Use the messaging features to send interests and chat with other users.   
   
