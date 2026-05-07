from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.message_schema import MessageCreateRequest, MessageListResponse, MessageResponse, SentMessageListResponse
from app.services.auth_service import get_current_user
from app.services.message_service import MessageService

router = APIRouter(prefix='/messages', tags=['Messages'])


@router.get('/conversation/{conversation_id}', response_model=MessageListResponse)
def list_conversation_messages(conversation_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return MessageService(db).list_conversation_messages(conversation_id, current_user)


@router.get('/sent/me', response_model=SentMessageListResponse)
def list_sent_messages(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return MessageService(db).list_sent_messages(current_user)


@router.post('', response_model=MessageResponse)
def create_message(payload: MessageCreateRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return MessageService(db).create_message(payload, current_user)
