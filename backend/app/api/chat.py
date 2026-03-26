"""
Chat endpoint — streams ADK agent responses as Server-Sent Events.
Session is created on first message and resumed on subsequent ones.
"""

import json
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.ai.agent import get_agent_runner

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    session_id: str | None = None
    scope: dict | None = None  # {"type": "source", "id": "..."} | {"type": "collection", "id": "..."} | None (all)


@router.post("/")
async def chat(body: ChatMessage, db: AsyncSession = Depends(get_db)):
    session_id = body.session_id or str(uuid.uuid4())
    runner = await get_agent_runner()

    async def event_stream():
        yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
        async for event in runner.run_async(
            user_id="user",
            session_id=session_id,
            message=body.message,
        ):
            if event.is_final_response():
                payload = {"type": "done", "text": event.text, "citations": []}
                yield f"data: {json.dumps(payload)}\n\n"
            elif hasattr(event, "text") and event.text:
                yield f"data: {json.dumps({'type': 'token', 'text': event.text})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/sessions")
async def list_sessions(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.adk_session import AdkSession
    result = await db.execute(select(AdkSession).order_by(AdkSession.updated_at.desc()))
    sessions = result.scalars().all()
    return [{"session_id": s.session_id, "updated_at": s.updated_at} for s in sessions]
