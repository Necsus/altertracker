from flask import Blueprint
from flask_socketio import emit, join_room
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import socketio, db
from app.models.message import Message

message_bp = Blueprint('message', __name__)

@socketio.on('connect_messaging')
def handle_connect():
    user_id = get_jwt_identity()
    join_room(str(user_id))
    emit('status', {'msg': 'Connected'}, room=str(user_id))

@socketio.on('private_message')
@jwt_required()
def handle_private_message(data):
    sender_id = get_jwt_identity()
    receiver_id = data['to']
    content = data['content']
    
    # Store message in DB
    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.session.add(message)
    db.session.commit()

    # Emit message to receiver
    emit('new_message', {
        'from': sender_id,
        'content': content,
        'timestamp': message.timestamp.isoformat()
    }, room=str(receiver_id))

@socketio.on('update_message_status')
@jwt_required()
def update_message_status(data):
    user_id = get_jwt_identity()
    message_id = data['message_id']
    status = data['status']  # 'delivered' ou 'read'

    message = db.session.query(Message).filter_by(id=message_id, receiver_id=user_id).first()
    if message:
        message.status = status
        db.session.commit()
        emit('message_status_updated', {
            'message_id': message_id,
            'status': status
        }, room=str(user_id))