from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.conversation_schema import ConversationListResponse, ConversationResponse, StartConversationRequest
from app.services.auth_service import get_current_user
from app.services.conversation_service import ConversationService

router = APIRouter(prefix='/conversations', tags=['Conversations'])


@router.get('', response_model=ConversationListResponse)
def list_conversations(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return ConversationService(db).list_conversations(current_user)


@router.get('/me', response_model=ConversationListResponse)
def list_my_conversations(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return ConversationService(db).list_conversations(current_user)


@router.get('/{conversation_id}', response_model=ConversationResponse)
def get_conversation(conversation_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return ConversationService(db).get_conversation(conversation_id, current_user)


@router.post('/start', response_model=ConversationResponse)
def start_conversation(payload: StartConversationRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return ConversationService(db).start_conversation(payload.productId, payload.message, current_user)
