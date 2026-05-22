from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

class User(db.Model, UserMixin):
    """
    User database model storing credentials, session IDs, and active tasks relationships.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship linking users to tasks. Cascades deletions automatically.
    tasks = db.relationship("Task", backref="assignee", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Hashes the user-provided password and saves it to password_hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies a plain-text password against the stored password hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Formats the model data as a serializable dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<User {self.username}>"

@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login callback helper to load a user object from the session storage.
    """
    return User.query.get(int(user_id))
