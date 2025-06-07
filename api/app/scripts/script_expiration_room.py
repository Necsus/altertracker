from datetime import datetime, timezone
from app.models.chat_room import ChatRoom, ChatRoomStatusEnum
from app.extensions import db

expired_rooms = ChatRoom.query.filter(
    ChatRoom.expiration_date < datetime.now(timezone.utc),
    ChatRoom.status == ChatRoomStatusEnum.ACTIVE
).all()

for room in expired_rooms:
    room.status = ChatRoomStatusEnum.EXPIRED

db.session.commit()