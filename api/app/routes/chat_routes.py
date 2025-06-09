from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_socketio import join_room
from app.models.card import Card
from app.models.user_collection import UserCollection
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
        (ChatRoom.seller_id == user_id) | (ChatRoom.buyer_id == user_id)
    ).order_by(ChatRoom.created_at.desc()).all()

    def room_to_dict(room):
        last_message = sorted(room.messages, key=lambda x: x.sent_at, reverse=True)[0] if room.messages else None
        card = Card.query.filter_by(reference=room.reference_card).first()
        if not card:
            return jsonify({"error": "Card not found"}), 404
        return {
            "id": str(room.id),
            "reference_card": room.reference_card,
            "card": card.json(),
            "status": room.status,
            "created_at": room.created_at.isoformat(),
            "messages": {
                "sender": 'me' if last_message.sender_id == user_id else 'other',
                "content": last_message.content,
                "sent_at": last_message.sent_at.isoformat()
            } if last_message else None
        }

    return jsonify([room_to_dict(room) for room in rooms])

@chat_bp.route('/message/<uuid:room_id>', methods=['GET'])
@jwt_required()
def get_messages(room_id):
    user_id = get_jwt_identity()
    room = ChatRoom.query.filter_by(id=room_id).first()

    if not room:
        return jsonify({"error": "Room not found"}), 404
    
    if room.seller_id != user_id and room.buyer_id != user_id:
        return jsonify({"error": "You are not a participant in this room"}), 403

    messages = ChatMessage.query.filter_by(room_id=room.id).order_by(ChatMessage.sent_at.asc()).all()

    def message_to_dict(message):
        return {
            "sender": 'me' if message.sender_id == user_id else 'other',
            "content": message.content,
            "sent_at": message.sent_at.isoformat()
        }

    return jsonify([message_to_dict(message) for message in messages])

@chat_bp.route('/message', methods=['POST'])
@jwt_required()
def receive_message():
    data = request.json
    sender_id = get_jwt_identity()
    content = data["content"]
    room_id = data["room_id"]

    room = ChatRoom.query.filter_by(id=room_id).first()

    if not room:
        return jsonify({"error": "Room not found"}), 404
    
    if room.seller_id != sender_id and room.buyer_id != sender_id:
        return jsonify({"error": "You are not a participant in this room"}), 403

    message = ChatMessage(room_id=room.id, sender_id=sender_id, content=content)
    db.session.add(message)
    db.session.commit()
    return jsonify({"status": "message_received"})

@chat_bp.route("/room/create/<int:purchase_id>", methods=["GET"])
@jwt_required()
def create_room(purchase_id: int):
    offer_purchase = db.session.query(OfferPurchase).filter_by(id=purchase_id).first()
    if not offer_purchase:
        return jsonify({"error": "Offer purchase not found"}), 404
    seller_id = get_jwt_identity()
    collection = UserCollection.query.filter_by(
        id_user=seller_id, 
        reference_card=offer_purchase.reference_card
    ).first()
    if not collection:
        return jsonify({"error": "Card not in your collection"}), 404
    room = ChatRoom(
        reference_card=offer_purchase.reference_card,
        seller_id=seller_id,
        buyer_id=offer_purchase.id_user,
        status='active',
        expiration_date=datetime.now(timezone.utc) + timedelta(days=7),
        seller_closed=False,
        buyer_closed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.session.add(room)
    offer_purchase.room_id = room.id
    db.session.commit()
    # socketio.emit("room_created", {
    #     "room_id": str(room.id),
    #     "user1_id": room.user1_id,
    #     "user2_id": room.user2_id
    # }, room=str(room.id))
    return jsonify({"status": "room created", "room_id": str(room.id)})

@chat_bp.route("/room/close/<uuid:room_id>", methods=["GET"])
@jwt_required()
def close_room(room_id):
    user_id = get_jwt_identity()

    room = ChatRoom.query.get_or_404(room_id)

    if user_id == room.seller_id:
        room.seller_closed = True
    elif user_id == room.buyer_id:
        room.buyer_closed = True

    if room.seller_closed and room.buyer_closed:
        room.status = ChatRoomStatusEnum.CLOSED.value

    db.session.commit()
    return jsonify({"status": "room_updated", "room": str(room.id)})

@socketio.on('join_room')
def handle_join(data):
    room_id = data.get("room_id")
    print(f"Joining room: {room_id}")
    join_room(room_id)
    socketio.emit("status", f"Joined room {room_id}", room=room_id)

@socketio.on('send_mesage')
def handle_send_message(data):
    room_id = data.get("room_id")
    content = data.get("content")
    sent_at = data.get("sent_at", datetime.now(timezone.utc).isoformat())
    socketio.emit('new_message', {
        "room_id": room_id,
        "sender": 'other',
        "content": content,
        "sent_at": sent_at
    }, room=str(room_id), include_self=False)