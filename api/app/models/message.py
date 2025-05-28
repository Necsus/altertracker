import datetime
from app.extensions import db

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    status = db.Column(db.String(20), default='sent')  # Possible values: 'sent', 'delivered', 'read'

    def __repr__(self):
        return f"<Message from {self.sender_id} to {self.receiver_id}>"

    def json(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'status': self.status
        }

    def __init__(self, sender_id, receiver_id, content, status='sent'):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.status = status
        self.timestamp = datetime.datetime.now(datetime.timezone.utc)