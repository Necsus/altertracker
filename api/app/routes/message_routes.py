from flask import Blueprint, jsonify
from flask_socketio import emit, join_room
from flask_jwt_extended import decode_token, get_jwt_identity, jwt_required
from app.extensions import socketio, db
from app.models.message import Message

message_bp = Blueprint('message', __name__)

@message_bp.route('/history/<int:selected_user_id>', methods=['GET'])
@jwt_required()
def get_message_history(selected_user_id):
    user_id = get_jwt_identity()  # Récupérer l'identité de l'utilisateur à partir du token JWT
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == selected_user_id)) |
        ((Message.sender_id == selected_user_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp.asc()).all()

    return jsonify([{
        'id': message.id,
        'from': message.sender_id,
        'to': message.receiver_id,
        'content': message.content,
        'timestamp': message.timestamp.isoformat(),
        'status': message.status
    } for message in messages])

@socketio.on('connect_messaging')
def handle_connect(data):
    token = data.get('token', '').replace('Bearer ', '')
    try:
        # Décoder et valider le token JWT
        decoded_token = decode_token(token)
        user_id = decoded_token['sub']  # Récupérer l'identité de l'utilisateur

        # Ajouter l'utilisateur à une room basée sur son ID
        join_room(str(user_id))
        emit('status', {'msg': 'Connected'}, room=str(user_id))
    except Exception as e:
        emit('error', {'msg': 'Authentication failed'})

@socketio.on('private_message')
def handle_private_message(data):
    token = data.get('token', '').replace('Bearer ', '')
    try:
        # Décoder et valider le token JWT
        decoded_token = decode_token(token)
        sender_id = decoded_token['sub']  # Récupérer l'identité de l'utilisateur
        print(sender_id)
        receiver_id = data['to']
        content = data['content']

        # Stocker le message dans la base de données
        message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
        db.session.add(message)
        db.session.commit()

        # Émettre le message au destinataire
        emit('new_message', {
            'from': sender_id,
            'content': content,
            'timestamp': message.timestamp.isoformat()
        }, room=str(receiver_id))
    except Exception as e:
        emit('error', {'msg': 'Authentication failed'})

@socketio.on('update_message_status')
def update_message_status(data):
    token = data.get('token', '').replace('Bearer ', '')
    try:
        decoded_token = decode_token(token)
        sender_id = decoded_token['sub']  # Récupérer l'identité de l'utilisateur
        message_id = data['message_id']
        status = data['status']  # 'delivered' ou 'read'

        message = db.session.query(Message).filter_by(id=message_id, receiver_id=sender_id).first()
        if message:
            message.status = status
            db.session.commit()
            emit('message_status_updated', {
                'message_id': message_id,
                'status': status
            }, room=str(sender_id))
    except Exception as e:
        emit('error', {'msg': 'Authentication failed'})