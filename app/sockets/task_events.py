from flask_socketio import join_room, leave_room
from flask_login import current_user
from app.extensions import socketio

@socketio.on("connect")
def handle_connect():
    """
    WebSocket connection callback.
    Puts the authenticated user into a private secure room named user_<user_id>.
    """
    if current_user.is_authenticated:
        room = f"user_{current_user.id}"
        join_room(room)
        print(f" * Socket Connection: User {current_user.username} joined room {room}")
    else:
        print(" * Socket Connection: Anonymous client connected")

@socketio.on("disconnect")
def handle_disconnect():
    """
    WebSocket disconnection callback.
    Removes the user from their private room on connection loss.
    """
    if current_user.is_authenticated:
        room = f"user_{current_user.id}"
        leave_room(room)
        print(f" * Socket Disconnection: User {current_user.username} left room {room}")
    else:
        print(" * Socket Disconnection: Anonymous client disconnected")
