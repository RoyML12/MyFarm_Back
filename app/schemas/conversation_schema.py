from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class StartConversationRequest(BaseModel):
    productId: int
    message: Optional[str] = None


class ConversationResponse(BaseModel):
    id: int
    productId: int
    productName: str
    productImage: Optional[str] = None
    seller: str
    sellerName: str
    buyerName: str
    buyerId: int
    sellerId: int
    role: Optional[str] = None
    otherUserName: Optional[str] = None
    lastMessage: Optional[str] = None
    lastMessageAt: Optional[datetime] = None
    unreadCount: int = 0
    createdAt: datetime
    updatedAt: datetime


class ConversationListResponse(BaseModel):
    total: int
    items: List[ConversationResponse]
