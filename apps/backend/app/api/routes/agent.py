from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.core.config import get_settings
from app.schemas.agent import ChatRequest
from app.services.agent.service import AgentService

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=None)
def agent_chat(
    payload: ChatRequest,
    session: Session = Depends(get_db_session),
):
    settings = get_settings()
    if not settings.openai_api_key:
        return JSONResponse(
            status_code=503,
            content={
                "type": "AgentUnavailable",
                "message": "AI agent is not configured. Set OPENAI_API_KEY to enable it.",
                "code": "agent_unavailable",
            },
        )

    conversation_id = payload.conversation_id or str(uuid4())

    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in payload.history
    ]
    messages.append({"role": "user", "content": payload.message})

    service = AgentService(session)

    return StreamingResponse(
        service.chat_stream(messages=messages, conversation_id=conversation_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Conversation-ID": conversation_id,
        },
    )
