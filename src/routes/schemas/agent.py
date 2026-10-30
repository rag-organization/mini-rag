from uuid import UUID

from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str | None = None
    conversation_id: UUID | None = None