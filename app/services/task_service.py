from app.extensions import db
from app.models.task import Task

class TaskService:
    @staticmethod
    def get_user_tasks(user_id, status=None, priority=None, search_query=None):
        """
        Retrieves all tasks belonging to a specific user.
        Supports optional filtering by status, priority, and text search query.
        """
        query = Task.query.filter_by(user_id=user_id)
        
        # Apply status filter
        if status:
            query = query.filter(Task.status == status.upper().strip())
            
        # Apply priority filter
        if priority:
            query = query.filter(Task.priority == priority.upper().strip())
            
        # Apply search query (fuzzy search across title and description)
        if search_query:
            search_format = f"%{search_query.strip()}%"
            query = query.filter(
                (Task.title.ilike(search_format)) | 
                (Task.description.ilike(search_format))
            )
            
        # Order by creation date (newest first)
        return query.order_by(Task.created_at.desc()).all()

    @staticmethod
    def get_task_by_id(user_id, task_id):
        """
        Retrieves a single task ensuring it belongs to the authenticated user.
        """
        return Task.query.filter_by(id=task_id, user_id=user_id).first()

    @staticmethod
    def create_task(user_id, title, description=None, priority="MEDIUM", status="PENDING"):
        """
        Creates and saves a new task.
        """
        if not title:
            raise ValueError("Task title is required")
            
        title = title.strip()
        priority = priority.upper().strip() if priority else "MEDIUM"
        status = status.upper().strip() if status else "PENDING"
        
        # Validate Enum values
        if priority not in ["LOW", "MEDIUM", "HIGH"]:
            raise ValueError("Priority must be one of: LOW, MEDIUM, HIGH")
        if status not in ["PENDING", "IN_PROGRESS", "COMPLETED"]:
            raise ValueError("Status must be one of: PENDING, IN_PROGRESS, COMPLETED")
            
        new_task = Task(
            user_id=user_id,
            title=title,
            description=description.strip() if description else None,
            priority=priority,
            status=status
        )
        
        db.session.add(new_task)
        db.session.commit()
        return new_task

    @staticmethod
    def update_task(user_id, task_id, title=None, description=None, priority=None, status=None):
        """
        Updates an existing task if it belongs to the user.
        """
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Task not found or access denied")
            
        # Update details if provided
        if title is not None:
            if not title.strip():
                raise ValueError("Task title cannot be empty")
            task.title = title.strip()
            
        if description is not None:
            task.description = description.strip() if description else None
            
        if priority is not None:
            priority = priority.upper().strip()
            if priority not in ["LOW", "MEDIUM", "HIGH"]:
                raise ValueError("Priority must be one of: LOW, MEDIUM, HIGH")
            task.priority = priority
            
        if status is not None:
            status = status.upper().strip()
            if status not in ["PENDING", "IN_PROGRESS", "COMPLETED"]:
                raise ValueError("Status must be one of: PENDING, IN_PROGRESS, COMPLETED")
            task.status = status
            
        db.session.commit()
        return task

    @staticmethod
    def delete_task(user_id, task_id):
        """
        Deletes a task ensuring ownership verification.
        """
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Task not found or access denied")
            
        db.session.delete(task)
        db.session.commit()
        return True
