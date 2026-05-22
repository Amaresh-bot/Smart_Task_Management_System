from flask_login import login_user, logout_user
from app.extensions import db
from app.models.user import User

class AuthService:
    @staticmethod
    def register(username, password):
        """
        Validates username availability and registers a new user.
        Raises ValueError if user already exists or inputs are invalid.
        """
        if not username or not password:
            raise ValueError("Username and password are required")
            
        username = username.strip()
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
            
        # Check if username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            raise ValueError("Username is already taken")
            
        # Create and persist new user
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def login(username, password):
        """
        Verifies login credentials.
        Returns the User instance if successful, else raises ValueError.
        """
        if not username or not password:
            raise ValueError("Username and password are required")
            
        user = User.query.filter_by(username=username.strip()).first()
        if not user or not user.check_password(password):
            raise ValueError("Invalid username or password")
            
        # Establish Flask-Login session
        login_user(user, remember=True)
        return user

    @staticmethod
    def logout():
        """
        Clears the user's active session.
        """
        logout_user()
        return True
