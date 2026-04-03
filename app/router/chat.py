import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import chat as crud
from app.models.chat import ChatSession, ChatMessage
from app.schemas.common import ResponseModel
from app.schemas.chat import ChatSend, ChatMessageOut, ChatSessionOut, ChatSource

router = APIRouter(prefix="/chat", tags=["chat"])


def _session_to_out(s: ChatSession) -> ChatSessionOut:
    return ChatSessionOut(
        id=s.id, title=s.title,
        createTime=s.created_at.isoformat() if s.created_at else "",
    )


def _message_to_out(m: ChatMessage) -> ChatMessageOut:
    sources = []
    if m.sources:
        try:
            sources = [ChatSource(**s) for s in json.loads(m.sources)]
        except (json.JSONDecodeError, TypeError):
            pass
    return ChatMessageOut(
        id=m.id, role=m.role, content=m.content, sources=sources,
        time=m.created_at.isoformat() if m.created_at else "",
    )


@router.post("/send")
async def send_message(body: ChatSend, db: AsyncSession = Depends(get_db)):
    session = await crud.get_session_by_id(db, body.sessionId)
    if not session:
        session = await crud.create_session(db, id=body.sessionId, title=body.content[:50])

    sources_json = json.dumps([s.model_dump() for s in body.sources], ensure_ascii=False)
    await crud.create_message(
        db, session_id=session.id, role="user",
        content=body.content, sources=sources_json,
    )

    # Generate AI response (placeholder)
    reply_content = f"收到您的问题：「{body.content}」\n\n这是一个占位回复，实际的AI回答将在接入大模型后生成。"
    await crud.create_message(
        db, session_id=session.id, role="assistant",
        content=reply_content, sources=sources_json,
    )
    await db.commit()

    return ResponseModel(data={"content": reply_content})


@router.get("/sessions")
async def get_sessions(db: AsyncSession = Depends(get_db)):
    sessions = await crud.get_all_sessions(db)
    return ResponseModel(data=[_session_to_out(s) for s in sessions])


@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    messages = await crud.get_session_messages(db, session_id)
    return ResponseModel(data=[_message_to_out(m) for m in messages])


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    session = await crud.get_session_by_id(db, session_id)
    if not session:
        return ResponseModel(code=404, message="会话不存在")
    await crud.delete_session(db, session)
    return ResponseModel(message="删除成功")
