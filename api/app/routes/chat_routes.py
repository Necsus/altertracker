from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.offer_purchase import OfferPurchase
from app.extensions import db, socketio
from app.models.chat_room import ChatRoom, ChatRoomStatusEnum
from app.models.chat_message import ChatMessage
from app.models.user import User
from datetime import datetime, timedelta, timezone

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/room', methods=['GET'])
@jwt_required()
def get_rooms():
    user_id = get_jwt_identity()
    rooms = ChatRoom.query.filter(
        (ChatRoom.user1_id == user_id) | (ChatRoom.user2_id == user_id)
    ).order_by(ChatRoom.created_at.desc()).all()

    def room_to_dict(room):
        return {
            "id": str(room.id),
            "user1_id": room.user1_id,
            "user2_id": room.user2_id,
            "status": room.status,
            "created_at": room.created_at.isoformat(),
            "messages": [{
                "sender_id": m.sender_id,
                "content": m.content,
                "sent_at": m.sent_at.isoformat()
            } for m in sorted(room.messages, key=lambda x: x.sent_at)]
        }

    return jsonify([room_to_dict(room) for room in rooms])

@chat_bp.route("/message", methods=["POST"])
def receive_message():
    data = request.json
    sender = data["sender_id"]
    receiver = data["receiver_id"]
    content = data["content"]

    room = ChatRoom.query.filter(
        ((ChatRoom.user1_id == sender) & (ChatRoom.user2_id == receiver)) |
        ((ChatRoom.user1_id == receiver) & (ChatRoom.user2_id == sender)),
        ChatRoom.status == ChatRoomStatusEnum.ACTIVE.value
    ).first()

    if not room:
        room = ChatRoom(
            user1_id=sender,
            user2_id=receiver,
            expiration_date=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.session.add(room)
        db.session.commit()

    message = ChatMessage(room_id=room.id, sender_id=sender, content=content)
    db.session.add(message)
    db.session.commit()

    socketio.emit("new_message", {
        "room_id": str(room.id),
        "sender_id": sender,
        "content": content,
        "sent_at": message.sent_at.isoformat()
    }, room=str(room.id))

    return jsonify({"status": "message_received"})

@chat_bp.route("/room/create/<int:purchase_id>", methods=["POST"])
@jwt_required()
def create_room(purchase_id: int):
    offer_purchase = OfferPurchase.query.filter_by(id=purchase_id).first()
    if not offer_purchase:
        return jsonify({"error": "Offer purchase not found"}), 404
    user_id = get_jwt_identity()
    room = ChatRoom(
        reference_card=offer_purchase.reference_card,
        user1_id=user_id,
        user2_id=offer_purchase.user_id,
        status='active',
        expiration_date=datetime.now(timezone.utc) + timedelta(days=7),
        user1_closed=False,
        user2_closed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.session.add(room)
    db.session.commit()
    # socketio.emit("room_created", {
    #     "room_id": str(room.id),
    #     "user1_id": room.user1_id,
    #     "user2_id": room.user2_id
    # }, room=str(room.id))
    return jsonify({"status": "room created"})

@chat_bp.route("/room/<uuid:room_id>/close", methods=["POST"])
def close_room(room_id):
    data = request.json
    user_id = data.get("user_id")

    room = ChatRoom.query.get_or_404(room_id)

    if user_id == room.user1_id:
        room.user1_closed = True
    elif user_id == room.user2_id:
        room.user2_closed = True

    if room.user1_closed and room.user2_closed:
        room.status = ChatRoomStatusEnum.CLOSED.value

    db.session.commit()
    return jsonify({"status": "room_updated", "room": str(room.id)})