from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_cors import CORS

# Initialize SQLAlchemy ORM
db = SQLAlchemy()

# Initialize Login Manager for session-based user authentication
login_manager = LoginManager()
login_manager.login_view = "auth.login_view"  # Redirect target for @login_required routes
login_manager.login_message_category = "warning"

# Initialize SocketIO for bi-directional live events
# async_mode is set to 'eventlet' (from our requirements.txt eventlet server)
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')

# Initialize Flask-Migrate for DB schema updates
migrate = Migrate()

# Initialize CORS to support cross-origin resource sharing if needed
cors = CORS()
