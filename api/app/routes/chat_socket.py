from flask_socketio import emit, join_room
from app.extensions import socketio

@socketio.on("join_room")
def handle_join(data):
    room_id = data.get("room_id")
    join_room(room_id)
    emit("status", f"Joined room {room_id}", room=room_id)

@socketio.on("send_message")
def handle_send(data):
    from app.models.chat_message import ChatMessage
    from app.extensions import db

    msg = ChatMessage(
        room_id=data["room_id"],
        sender_id=data["sender_id"],
        content=data["content"]
    )
    db.session.add(msg)
    db.session.commit()

    emit("new_message", {
        "room_id": data["room_id"],
        "sender_id": data["sender_id"],
        "content": data["content"],
        "sent_at": msg.sent_at.isoformat()
    }, room=data["room_id"])