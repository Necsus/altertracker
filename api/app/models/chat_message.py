from datetime import datetime, timezone
import uuid
from sqlalchemy import UUID, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.extensions import db

class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = db.Column(UUID(as_uuid=True), ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    sender_id = db.Column(String, nullable=False)  # Discord ID
    content = db.Column(Text, nullable=False)
    sent_at = db.Column(DateTime, default=datetime.now(timezone.utc))

    room = relationship("ChatRoom", back_populates="messages")

from sqlalchemy import Index

Index("ix_chat_messages_room_id", ChatMessage.room_id)
Index("ix_chat_messages_sender_id", ChatMessage.sender_id)