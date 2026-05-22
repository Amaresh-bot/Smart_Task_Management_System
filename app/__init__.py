import os
from flask import Flask, redirect, url_for
from app.config import config_by_name
from app.extensions import db, login_manager, socketio, migrate, cors

def create_app(config_name=None):
    """
    Application Factory Pattern for initializing the Flask app.
    Loads configurations, boots extensions, hooks Blueprints and WebSockets.
    """
    if not config_name:
        config_name = os.getenv("FLASK_ENV", "development")
        
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cors.init_app(app)
    
    # Initialize SocketIO
    socketio.init_app(app)
    
    # Register SocketIO event handlers by importing them
    # This ensures decorators are loaded and recognized by Flask-SocketIO
    with app.app_context():
        from app.sockets import task_events
    
    # Register Flask Blueprints
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    
    # Root route redirect helper
    @app.route("/")
    def index():
        """Redirects root URL directly to the tasks dashboard."""
        return redirect(url_for("tasks.dashboard_view"))
        
    return app
