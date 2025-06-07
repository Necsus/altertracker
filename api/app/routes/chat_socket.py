from flask_socketio import SocketIO, join_room, leave_room, emit
from flask import request
from app.models.chat_message import ChatMessage
from app.models.chat_room import ChatRoom, ChatRoomStatusEnum
from app.extensions import socketio, db
from datetime import datetime, timezone
import uuid

@socketio.on("connect")
def on_connect():
    print("Socket connected:", request.sid)

@socketio.on("join_rooms")
def on_join_rooms(data):
    discord_id = data.get("discord_id")
    if not discord_id:
        return

    rooms = ChatRoom.query.filter(
        (ChatRoom.user1_id == discord_id) | (ChatRoom.user2_id == discord_id),
        ChatRoom.status == ChatRoomStatusEnum.ACTIVE
    ).all()

    for room in rooms:
        join_room(str(room.id))
    emit("rooms_joined", {"rooms": [str(r.id) for r in rooms]})

@socketio.on("send_message")
def on_send_message(data):
    room_id = data.get("room_id")
    sender_id = data.get("sender_id")
    content = data.get("content")

    room = ChatRoom.query.get(uuid.UUID(room_id))
    if not room or room.status != ChatRoomStatusEnum.ACTIVE:
        emit("error", {"message": "Room not available"})
        return

    message = ChatMessage(
        room_id=room.id,
        sender_id=sender_id,
        content=content,
        sent_at=datetime.now(timezone.utc)
    )
    db.session.add(message)
    db.session.commit()

    # Diffuse aux utilisateurs dans la room
    emit("new_message", {
        "room_id": room_id,
        "sender_id": sender_id,
        "content": content,
        "sent_at": message.sent_at.isoformat()
    }, room=room_id)

@socketio.on("disconnect")
def on_disconnect():
    print("Socket disconnected:", request.sid)