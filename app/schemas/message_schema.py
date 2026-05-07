from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class MessageCreateRequest(BaseModel):
    conversationId: int
    message: str = Field(min_length=1)


class MessageResponse(BaseModel):
    id: int
    conversationId: int
    senderId: int
    senderName: str
    message: str
    isRead: bool
    createdAt: datetime


class MessageListResponse(BaseModel):
    total: int
    items: List[MessageResponse]


class SentMessageSummaryResponse(BaseModel):
    id: int
    productId: int
    productName: str
    productImage: str | None = None
    seller: str
    breed: str
    typeMaterial: str
    message: str
    createdAt: datetime


class SentMessageListResponse(BaseModel):
    total: int
    items: List[SentMessageSummaryResponse]
