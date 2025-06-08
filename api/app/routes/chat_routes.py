from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
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
        return {
            "id": str(room.id),
            "reference_card": room.reference_card,
            # "seller_id": room.seller_id,
            # "buyer_id": room.buyer_id,
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
        ((ChatRoom.seller_id == sender) & (ChatRoom.buyer_id == receiver)) |
        ((ChatRoom.seller_id == receiver) & (ChatRoom.buyer_id == sender)),
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

@chat_bp.route("/room/create/<int:purchase_id>", methods=["GET"])
@jwt_required()
def create_room(purchase_id: int):
    offer_purchase = OfferPurchase.query.filter_by(id=purchase_id).first()
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
    db.session.commit()
    # socketio.emit("room_created", {
    #     "room_id": str(room.id),
    #     "user1_id": room.user1_id,
    #     "user2_id": room.user2_id
    # }, room=str(room.id))
    return jsonify({"status": "room created", "room_id": str(room.id)})

@chat_bp.route("/room/<uuid:room_id>/close", methods=["POST"])
def close_room(room_id):
    data = request.json
    user_id = data.get("user_id")

    room = ChatRoom.query.get_or_404(room_id)

    if user_id == room.seller_id:
        room.seller_closed = True
    elif user_id == room.buyer_id:
        room.buyer_closed = True

    if room.seller_closed and room.buyer_closed:
        room.status = ChatRoomStatusEnum.CLOSED.value

    db.session.commit()
    return jsonify({"status": "room_updated", "room": str(room.id)})