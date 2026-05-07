from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.conversation_schema import ConversationResponse


class ConversationService:
    def __init__(self, db: Session):
        self.conversation_repo = ConversationRepository(db)
        self.message_repo = MessageRepository(db)
        self.product_repo = ProductRepository(db)

    @staticmethod
    def serialize_conversation(conversation, current_user_id: int | None = None) -> ConversationResponse:
        messages = sorted(list(conversation.messages or []), key=lambda item: (item.created_at, item.id))
        last_message = messages[-1] if messages else None
        seller_name = conversation.seller_user.full_name if conversation.seller_user else 'Vendedor'
        buyer_name = conversation.buyer.full_name if conversation.buyer else 'Comprador'

        role = None
        other_user_name = None
        unread_count = 0
        if current_user_id:
            if current_user_id == conversation.seller_id:
                role = 'seller'
                other_user_name = buyer_name
            elif current_user_id == conversation.buyer_id:
                role = 'buyer'
                other_user_name = seller_name

            unread_count = sum(
                1
                for message in messages
                if message.sender_id != current_user_id and not bool(message.is_read)
            )

        return ConversationResponse(
            id=conversation.id,
            productId=conversation.product_id,
            productName=conversation.product.name if conversation.product else 'Producto',
            productImage=conversation.product.image_url if conversation.product else None,
            seller=seller_name,
            sellerName=seller_name,
            buyerName=buyer_name,
            buyerId=conversation.buyer_id,
            sellerId=conversation.seller_id,
            role=role,
            otherUserName=other_user_name,
            lastMessage=last_message.message if last_message else None,
            lastMessageAt=last_message.created_at if last_message else None,
            unreadCount=unread_count,
            createdAt=conversation.created_at,
            updatedAt=conversation.updated_at,
        )

    def start_conversation(self, product_id: int, initial_message: str | None, current_user):
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Producto no encontrado')
        if product.seller_id == current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No puedes iniciar una conversación con tu propio producto')

        conversation = self.conversation_repo.get_by_unique(product_id, current_user.id, product.seller_id)
        if not conversation:
            conversation = self.conversation_repo.create(product_id=product_id, buyer_id=current_user.id, seller_id=product.seller_id)
        if initial_message and initial_message.strip():
            self.message_repo.create(conversation_id=conversation.id, sender_id=current_user.id, message=initial_message.strip())
            conversation = self.conversation_repo.get_by_id(conversation.id)
        return self.serialize_conversation(conversation, current_user.id)

    def list_conversations(self, current_user):
        conversations = self.conversation_repo.list_for_user(current_user.id)
        items = [self.serialize_conversation(item, current_user.id) for item in conversations]
        items.sort(key=lambda item: item.lastMessageAt or item.updatedAt or item.createdAt, reverse=True)
        return {'total': len(items), 'items': items}

    def get_conversation(self, conversation_id: int, current_user):
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Conversación no encontrada')
        if current_user.id not in {conversation.buyer_id, conversation.seller_id}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No puedes ver esta conversación')
        return self.serialize_conversation(conversation, current_user.id)
