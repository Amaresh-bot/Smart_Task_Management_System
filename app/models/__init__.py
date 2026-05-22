from app.extensions import db

# Import models here so SQLAlchemy registers them on metadata
from app.models.user import User
from app.models.task import Task

__all__ = ["db", "User", "Task"]
