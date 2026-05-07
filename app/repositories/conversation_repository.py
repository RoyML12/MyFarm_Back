from sqlalchemy.orm import Session, joinedload

from app.models.conversation_model import Conversation
from app.models.message_model import Message
from app.models.product_model import Product


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_unique(self, product_id: int, buyer_id: int, seller_id: int):
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.product_id == product_id,
                Conversation.buyer_id == buyer_id,
                Conversation.seller_id == seller_id,
            )
            .first()
        )

    def get_by_id(self, conversation_id: int):
        return (
            self.db.query(Conversation)
            .options(
                joinedload(Conversation.product).joinedload(Product.certifications),
                joinedload(Conversation.buyer),
                joinedload(Conversation.seller_user),
                joinedload(Conversation.messages).joinedload(Message.sender),
            )
            .filter(Conversation.id == conversation_id)
            .first()
        )

    def list_for_user(self, user_id: int):
        return (
            self.db.query(Conversation)
            .options(
                joinedload(Conversation.product),
                joinedload(Conversation.buyer),
                joinedload(Conversation.seller_user),
                joinedload(Conversation.messages).joinedload(Message.sender),
            )
            .filter((Conversation.buyer_id == user_id) | (Conversation.seller_id == user_id))
            .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
            .all()
        )

    def create(self, *, product_id: int, buyer_id: int, seller_id: int):
        conversation = Conversation(product_id=product_id, buyer_id=buyer_id, seller_id=seller_id)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return self.get_by_id(conversation.id)
