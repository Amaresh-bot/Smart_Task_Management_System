from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)

# ==========================================
# VIEW ROUTES (HTML Page Renderers)
# ==========================================

@auth_bp.route("/login", methods=["GET"])
def login_view():
    """Renders the login HTML interface. Redirects if already authenticated."""
    if current_user.is_authenticated:
        return redirect(url_for("tasks.dashboard_view"))
    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET"])
def register_view():
    """Renders the registration HTML interface. Redirects if already authenticated."""
    if current_user.is_authenticated:
        return redirect(url_for("tasks.dashboard_view"))
    return render_template("auth/register.html")


# ==========================================
# REST API ENDPOINTS
# ==========================================

@auth_bp.route("/api/auth/register", methods=["POST"])
def api_register():
    """
    REST API endpoint for User Registration.
    Expects JSON body with 'username' and 'password'.
    """
    # Accept both JSON payload and standard form payloads (for extreme versatility)
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form or {}
        
    username = data.get("username")
    password = data.get("password")
    
    try:
        new_user = AuthService.register(username, password)
        return jsonify({
            "status": "success",
            "message": "User registered successfully! Please log in.",
            "user": new_user.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An unexpected server error occurred during registration."
        }), 500


@auth_bp.route("/api/auth/login", methods=["POST"])
def api_login():
    """
    REST API endpoint for User Login.
    Expects JSON body with 'username' and 'password'.
    Establishes secure cookie session.
    """
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form or {}
        
    username = data.get("username")
    password = data.get("password")
    
    try:
        user = AuthService.login(username, password)
        return jsonify({
            "status": "success",
            "message": f"Welcome back, {user.username}!",
            "user": user.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 401
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An unexpected server error occurred during login."
        }), 500


@auth_bp.route("/api/auth/logout", methods=["GET", "POST"])
def api_logout():
    """
    REST API / Action endpoint for User Logout.
    Clears active user session.
    """
    AuthService.logout()
    
    # Check if client expects JSON (AJAX) or redirection
    if request.is_json or "application/json" in request.headers.get("Accept", ""):
        return jsonify({
            "status": "success",
            "message": "Logged out successfully"
        }), 200
        
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login_view"))


@auth_bp.route("/api/auth/me", methods=["GET"])
def api_current_user():
    """
    Retrieves currently authenticated user details.
    """
    if not current_user.is_authenticated:
        return jsonify({
            "status": "unauthenticated",
            "message": "No active session found"
        }), 401
        
    return jsonify({
        "status": "authenticated",
        "user": current_user.to_dict()
    }), 200
