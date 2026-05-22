from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_cors import CORS

# Initialize SQLAlchemy ORM
db = SQLAlchemy()

# Initialize Login Manager for session-based user authentication
login_manager = LoginManager()
login_manager.login_view = "auth.login_view"
login_manager.login_message_category = "warning"

# Initialize SocketIO for real-time communication
# Using threading mode for Render compatibility
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading"
)

# Initialize Flask-Migrate for DB schema updates
migrate = Migrate()

# Initialize CORS support
cors = CORS()
