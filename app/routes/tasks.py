from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.services.task_service import TaskService
from app.services.analytics_service import AnalyticsService
from app.extensions import socketio

tasks_bp = Blueprint("tasks", __name__)

# ==========================================
# VIEW ROUTES (HTML Page Renderers)
# ==========================================

@tasks_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard_view():
    """Renders the main task dashboard interface."""
    return render_template("tasks/dashboard.html", user=current_user)

@tasks_bp.route("/analytics", methods=["GET"])
@login_required
def analytics_view():
    """Renders the task analytics visual dashboard."""
    return render_template("tasks/analytics.html", user=current_user)


# ==========================================
# REST API ENDPOINTS (JSON)
# ==========================================

@tasks_bp.route("/api/tasks", methods=["GET"])
@login_required
def api_get_tasks():
    """
    REST API to fetch all tasks for the logged-in user.
    Supports optional filters: ?status=PENDING&priority=HIGH&search=clean
    """
    status = request.args.get("status")
    priority = request.args.get("priority")
    search = request.args.get("search")
    
    try:
        tasks = TaskService.get_user_tasks(
            user_id=current_user.id,
            status=status,
            priority=priority,
            search_query=search
        )
        return jsonify({
            "status": "success",
            "count": len(tasks),
            "tasks": [task.to_dict() for task in tasks]
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve tasks"
        }), 500


@tasks_bp.route("/api/tasks", methods=["POST"])
@login_required
def api_create_task():
    """
    REST API to create a new task.
    Expects JSON body with 'title', and optional 'description', 'priority', 'status'.
    Triggers Socket.IO live notifications.
    """
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form or {}
        
    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority", "MEDIUM")
    status = data.get("status", "PENDING")
    
    try:
        new_task = TaskService.create_task(
            user_id=current_user.id,
            title=title,
            description=description,
            priority=priority,
            status=status
        )
        
        task_data = new_task.to_dict()
        
        # WebSocket live emit: notifies client to append task in real-time
        # Scoped to user id by broadcasting to room user_<id>
        socketio.emit(
            "task_event",
            {"action": "create", "task": task_data},
            to=f"user_{current_user.id}"
        )
        
        return jsonify({
            "status": "success",
            "message": "Task created successfully",
            "task": task_data
        }), 201
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to create task"
        }), 500


@tasks_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
@login_required
def api_update_task(task_id):
    """
    REST API to update an existing task.
    Expects JSON body containing fields to edit.
    Triggers Socket.IO live notifications.
    """
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form or {}
        
    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority")
    status = data.get("status")
    
    try:
        updated_task = TaskService.update_task(
            user_id=current_user.id,
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            status=status
        )
        
        task_data = updated_task.to_dict()
        
        # WebSocket live emit: notifies client to update interface dynamically
        socketio.emit(
            "task_event",
            {"action": "update", "task": task_data},
            to=f"user_{current_user.id}"
        )
        
        return jsonify({
            "status": "success",
            "message": "Task updated successfully",
            "task": task_data
        }), 200
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to update task"
        }), 500


@tasks_bp.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def api_delete_task(task_id):
    """
    REST API to delete a task.
    Triggers Socket.IO live notifications.
    """
    try:
        TaskService.delete_task(user_id=current_user.id, task_id=task_id)
        
        # WebSocket live emit: notifies client to remove task item
        socketio.emit(
            "task_event",
            {"action": "delete", "task_id": task_id},
            to=f"user_{current_user.id}"
        )
        
        return jsonify({
            "status": "success",
            "message": "Task deleted successfully"
        }), 200
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to delete task"
        }), 500


@tasks_bp.route("/api/tasks/analytics", methods=["GET"])
@login_required
def api_get_analytics():
    """
    REST API endpoint returning computed statistics and KPI metrics 
    calculated via Pandas and NumPy for the logged-in user.
    """
    try:
        stats = AnalyticsService.get_task_statistics(current_user.id)
        return jsonify({
            "status": "success",
            "analytics": stats
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to calculate analytics metrics"
        }), 500
