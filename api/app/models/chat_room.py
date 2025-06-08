from enum import Enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.extensions import db  # Remplace avec ton import

class ChatRoomStatusEnum(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    EXPIRED = "expired"

class ChatRoom(db.Model):
    __tablename__ = "chat_rooms"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_card = db.Column(String, nullable=False)
    seller_id = db.Column(String, nullable=False)
    buyer_id = db.Column(String, nullable=False)

    status = db.Column(SQLAlchemyEnum(ChatRoomStatusEnum, values_callable=lambda obj: [e.value for e in obj]), 
                      nullable=False, 
                      default=ChatRoomStatusEnum.ACTIVE.value)
    expiration_date = db.Column(DateTime, nullable=False)

    seller_closed = db.Column(Boolean, default=False)
    buyer_closed = db.Column(Boolean, default=False)

    created_at = db.Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")

from sqlalchemy import Index

Index("ix_chat_rooms_seller_id", ChatRoom.seller_id)
Index("ix_chat_rooms_buyer_id", ChatRoom.buyer_id)