from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.conversation_model import Conversation
from app.models.message_model import Message


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, conversation_id: int, sender_id: int, message: str):
        item = Message(conversation_id=conversation_id, sender_id=sender_id, message=message)
        self.db.add(item)
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.updated_at = func.now()
        self.db.commit()
        self.db.refresh(item)
        return self.get_by_id(item.id)

    def get_by_id(self, message_id: int):
        return self.db.query(Message).options(joinedload(Message.sender)).filter(Message.id == message_id).first()

    def list_by_conversation(self, conversation_id: int):
        return (
            self.db.query(Message)
            .options(joinedload(Message.sender))
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
            .all()
        )

    def mark_as_read_for_user(self, *, conversation_id: int, user_id: int):
        self.db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id,
            Message.is_read == False,  # noqa: E712
        ).update({Message.is_read: True}, synchronize_session=False)
        self.db.commit()

    def list_sent_by_user(self, user_id: int):
        return (
            self.db.query(Message)
            .options(
                joinedload(Message.conversation).joinedload(Conversation.product),
                joinedload(Message.conversation).joinedload(Conversation.seller_user),
                joinedload(Message.sender),
            )
            .filter(Message.sender_id == user_id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .all()
        )
