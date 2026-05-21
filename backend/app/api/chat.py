from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.database import get_db
from app.llm.assistant import RestaurantAssistant, ChatSession

router = APIRouter(prefix="/api/chat", tags=["chat"])
limiter = Limiter(key_func=get_remote_address)

_assistant = RestaurantAssistant()

# In-memory sessions keyed by session_id (sufficient for demo)
_sessions: dict[str, ChatSession] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    message_count: int


@router.post("/", response_model=ChatResponse)
@limiter.limit("20/minute")
def chat(request: Request, body: ChatRequest, db: Session = Depends(get_db)):
    session = _sessions.setdefault(body.session_id, ChatSession())
    reply = _assistant.chat(db, session, body.message)
    return ChatResponse(
        session_id=body.session_id,
        reply=reply,
        message_count=len(session.messages),
    )


@router.delete("/{session_id}")
def clear_session(session_id: str):
    _sessions.pop(session_id, None)
    return {"status": "cleared"}
