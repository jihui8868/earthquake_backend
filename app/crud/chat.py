from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatSession, ChatMessage


async def get_session_by_id(db: AsyncSession, session_id: str) -> ChatSession | None:
    return await db.get(ChatSession, session_id)


async def create_session(db: AsyncSession, *, id: str, title: str = "新对话") -> ChatSession:
    session = ChatSession(id=id, title=title)
    db.add(session)
    await db.flush()
    return session


async def get_all_sessions(db: AsyncSession) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession).order_by(ChatSession.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_session(db: AsyncSession, session: ChatSession) -> None:
    await db.delete(session)
    await db.commit()


async def create_message(db: AsyncSession, *, session_id: str, role: str,
                          content: str, sources: str = "[]") -> ChatMessage:
    msg = ChatMessage(
        session_id=session_id, role=role,
        content=content, sources=sources,
    )
    db.add(msg)
    return msg


async def get_session_messages(db: AsyncSession, session_id: str) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    return list(result.scalars().all())
