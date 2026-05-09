from flask_login import current_user
from flask_socketio import emit, join_room, leave_room


def user_room(user_id: int) -> str:
    return f"user_{user_id}"


def register_socket_events(socketio):
    """Register Socket.IO events for authenticated dashboard sessions."""

    @socketio.on("connect")
    def handle_connect():
        if not current_user.is_authenticated:
            # Reject unauthenticated socket connections.
            return False

        room_name = user_room(current_user.id)
        join_room(room_name)
        emit(
            "socket_connected",
            {
                "message": "Real-time notifications connected.",
                "room": room_name,
            },
        )

    @socketio.on("disconnect")
    def handle_disconnect():
        if current_user.is_authenticated:
            leave_room(user_room(current_user.id))
