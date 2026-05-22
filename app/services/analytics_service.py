import pandas as pd
import numpy as np
from datetime import datetime
from app.models.task import Task

class AnalyticsService:
    @staticmethod
    def get_task_statistics(user_id):
        """
        Retrieves raw task database records for a user, loads them into a Pandas DataFrame,
        and computes advanced KPIs, ratios, and distributions utilizing Pandas and NumPy.
        """
        # Fetch tasks belonging to the user
        tasks = Task.query.filter_by(user_id=user_id).all()
        
        # Default fallback structure for new users with no tasks
        default_stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "inprogress_tasks": 0,
            "completion_rate": 0.0,
            "avg_priority_intensity": 0.0,
            "priority_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0},
            "status_distribution": {"PENDING": 0, "IN_PROGRESS": 0, "COMPLETED": 0},
            "backlog_intensity_description": "Clean Backlog"
        }
        
        if not tasks:
            return default_stats
            
        # Serialize database object list into a list of dictionaries for Pandas loading
        task_data = [task.to_dict() for task in tasks]
        
        # Load data into Pandas DataFrame
        df = pd.DataFrame(task_data)
        
        # 1. Total counts using Pandas size/len
        total_tasks = len(df)
        
        # 2. Count statuses by boolean mapping and summing with NumPy/Pandas
        completed_tasks = int(np.sum(df["status"] == "COMPLETED"))
        pending_tasks = int(np.sum(df["status"] == "PENDING"))
        inprogress_tasks = int(np.sum(df["status"] == "IN_PROGRESS"))
        
        # 3. Calculate Completion Rate using NumPy
        completion_rate = float(np.round((completed_tasks / total_tasks) * 100, 2))
        
        # 4. Distribution counts using Pandas value_counts
        status_counts = df["status"].value_counts().to_dict()
        priority_counts = df["priority"].value_counts().to_dict()
        
        # Ensure all category keys are represented in output distributions
        for status_key in ["PENDING", "IN_PROGRESS", "COMPLETED"]:
            if status_key not in status_counts:
                status_counts[status_key] = 0
                
        for priority_key in ["LOW", "MEDIUM", "HIGH"]:
            if priority_key not in priority_counts:
                priority_counts[priority_key] = 0
        
        # 5. Advanced analytics using NumPy: Average Priority Intensity Score
        # Low = 1.0, Medium = 2.0, High = 3.0
        # This computes the gravity of the user's workload backlog.
        priority_weights = {"LOW": 1.0, "MEDIUM": 2.0, "HIGH": 3.0}
        
        # Map the priority column to its numerical weight values
        df["priority_weight"] = df["priority"].map(priority_weights)
        
        # Exclude completed tasks from workload intensity (focus only on active backlog)
        active_backlog_df = df[df["status"] != "COMPLETED"]
        
        if not active_backlog_df.empty:
            # Calculate the average weight using NumPy mean
            avg_priority_intensity = float(np.round(np.mean(active_backlog_df["priority_weight"]), 2))
            
            # Map average scores to descriptions
            if avg_priority_intensity <= 1.5:
                backlog_intensity_description = "Low Workload Stress"
            elif avg_priority_intensity <= 2.5:
                backlog_intensity_description = "Balanced Workload Stress"
            else:
                backlog_intensity_description = "High Workload Stress (Action Required)"
        else:
            avg_priority_intensity = 0.0
            backlog_intensity_description = "All Workload Cleared"

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "inprogress_tasks": inprogress_tasks,
            "completion_rate": completion_rate,
            "avg_priority_intensity": avg_priority_intensity,
            "priority_distribution": priority_counts,
            "status_distribution": status_counts,
            "backlog_intensity_description": backlog_intensity_description
        }
