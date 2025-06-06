import datetime
from app.extensions import db

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String, nullable=False)
    sender_id = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    def to_dict(self):
        return {
            "sender_id": self.sender_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }