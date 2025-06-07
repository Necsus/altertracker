from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.chat_message import ChatMessage
from app.models.chat_room import ChatRoom, ChatRoomStatusEnum
from sqlalchemy.orm import joinedload
from app.models.user import User
from app.extensions import db

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")

# GET /api/chat/rooms/<discord_id>
@chat_bp.route("/rooms", methods=["GET"])
@jwt_required()
def get_user_rooms():
    id_user = get_jwt_identity()
    user = User.query.get(id_user)
    if not user or not user.discord_id:
        abort(404, "User not found or Discord ID not linked")
    discord_id = user.discord_id
    rooms = ChatRoom.query.filter(
        (ChatRoom.user1_id == discord_id) | (ChatRoom.user2_id == discord_id)
    ).all()
    return jsonify([{
        "id": str(r.id),
        "other_user": r.user2_id if r.user1_id == discord_id else r.user1_id,
        "status": r.status,
        "expires_at": r.expiration_date.isoformat(),
        "closed": r.user1_closed if r.user1_id == discord_id else r.user2_closed
    } for r in rooms])

# GET /api/chat/messages/<room_id>
@chat_bp.route("/messages/<uuid:room_id>", methods=["GET"])
@jwt_required()
def get_room_messages(room_id):
    id_user = get_jwt_identity()
    user = User.query.get(id_user)
    if not user or not user.discord_id:
        abort(404, "User not found or Discord ID not linked")
    discord_id = user.discord_id
    room = ChatRoom.query.options(joinedload(ChatRoom.messages)).filter_by(id=room_id).first()
    if not room:
        abort(404, "Room not found")
    if room.user1_id != discord_id and room.user2_id != discord_id:
        abort(403, "You are not a participant in this room")
    return jsonify([{
        "id": str(m.id),
        "sender_id": m.sender_id,
        "content": m.content,
        "sent_at": m.sent_at.isoformat()
    } for m in room.messages])

# POST /api/chat/messages/<room_id>
@chat_bp.route("/messages/<uuid:room_id>", methods=["POST"])
@jwt_required()
def post_message(room_id):
    id_user = get_jwt_identity()
    user = User.query.get(id_user)
    if not user or not user.discord_id:
        abort(404, "User not found or Discord ID not linked")
    discord_id = user.discord_id

    room = ChatRoom.query.get(room_id)
    if not room or room.status != ChatRoomStatusEnum.ACTIVE:
        abort(403, "Room not available")
    if room.user1_id != discord_id and room.user2_id != discord_id:
        abort(403, "You are not a participant in this room")

    data = request.json
    content = data.get("content")

    msg = ChatMessage(
        room_id=room_id,
        sender_id=discord_id,
        content=content
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"status": "sent", "id": str(msg.id)}), 201

# POST /api/chat/rooms/<room_id>/close
@chat_bp.route("/rooms/<uuid:room_id>/close", methods=["POST"])
@jwt_required()
def close_room(room_id):
    id_user = get_jwt_identity()
    user = User.query.get(id_user)
    if not user or not user.discord_id:
        abort(404, "User not found or Discord ID not linked")
    discord_id = user.discord_id

    data = request.json
    discord_id = data.get("discord_id")

    room = ChatRoom.query.get(room_id)
    if not room:
        abort(404)
    if room.user1_id != discord_id and room.user2_id != discord_id:
        abort(403, "You are not a participant in this room")

    if discord_id == room.user1_id:
        room.user1_closed = True
    elif discord_id == room.user2_id:
        room.user2_closed = True
    else:
        abort(403)

    # Si les 2 ont validé, on ferme
    if room.user1_closed and room.user2_closed:
        room.status = ChatRoomStatusEnum.CLOSED

    db.session.commit()
    return jsonify({"status": room.status})