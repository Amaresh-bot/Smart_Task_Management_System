import os
from app import create_app
from app.extensions import socketio

# Create the application instance via factory pattern
app = create_app()

if __name__ == "__main__":
    # Fetch parameters from the environment configuration
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    
    print(f" * Starting Smart Task Manager with real-time WebSockets on http://{host}:{port}")
    
    # Run the application through Flask-SocketIO server runner
    # This automatically leverages eventlet for premium concurrent async requests
    socketio.run(app, host=host, port=port, debug=debug)
