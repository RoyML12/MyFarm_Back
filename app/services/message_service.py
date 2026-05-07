from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.message_schema import MessageResponse, SentMessageSummaryResponse


class MessageService:
    def __init__(self, db: Session):
        self.message_repo = MessageRepository(db)
        self.conversation_repo = ConversationRepository(db)

    @staticmethod
    def serialize_message(message) -> MessageResponse:
        return MessageResponse(
            id=message.id,
            conversationId=message.conversation_id,
            senderId=message.sender_id,
            senderName=message.sender.full_name if message.sender else 'Usuario',
            message=message.message,
            isRead=bool(message.is_read),
            createdAt=message.created_at,
        )

    def list_conversation_messages(self, conversation_id: int, current_user):
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Conversación no encontrada')
        if current_user.id not in {conversation.buyer_id, conversation.seller_id}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No puedes ver estos mensajes')

        self.message_repo.mark_as_read_for_user(conversation_id=conversation_id, user_id=current_user.id)
        messages = self.message_repo.list_by_conversation(conversation_id)
        items = [self.serialize_message(item) for item in messages]
        return {'total': len(items), 'items': items}

    def create_message(self, payload, current_user):
        conversation = self.conversation_repo.get_by_id(payload.conversationId)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Conversación no encontrada')
        if current_user.id not in {conversation.buyer_id, conversation.seller_id}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No puedes enviar mensajes a esta conversación')

        message_text = payload.message.strip()
        if not message_text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='El mensaje no puede estar vacío')

        item = self.message_repo.create(conversation_id=payload.conversationId, sender_id=current_user.id, message=message_text)
        return self.serialize_message(item)

    def list_sent_messages(self, current_user):
        messages = self.message_repo.list_sent_by_user(current_user.id)
        items = []
        for item in messages:
            if not item.conversation or not item.conversation.product:
                continue
            product = item.conversation.product
            seller = item.conversation.seller_user
            items.append(
                SentMessageSummaryResponse(
                    id=item.id,
                    productId=product.id,
                    productName=product.name,
                    productImage=product.image_url,
                    seller=seller.full_name if seller else 'Vendedor',
                    breed=product.breed,
                    typeMaterial=product.type_material,
                    message=item.message,
                    createdAt=item.created_at,
                )
            )
        return {'total': len(items), 'items': items}
