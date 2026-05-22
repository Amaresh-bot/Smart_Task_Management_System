from datetime import datetime
from app.extensions import db

class Task(db.Model):
    """
    Task database model containing features like priorities, statuses, and links to users.
    """
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Priority states: LOW, MEDIUM, HIGH
    priority = db.Column(db.String(20), default="MEDIUM", nullable=False, index=True)
    
    # Status states: PENDING, IN_PROGRESS, COMPLETED
    status = db.Column(db.String(20), default="PENDING", nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key referring back to owner User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    def to_dict(self):
        """Serializes the Task object data to a clean dictionary format."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id
        }

    def __repr__(self):
        return f"<Task {self.id}: {self.title} ({self.status})>"
