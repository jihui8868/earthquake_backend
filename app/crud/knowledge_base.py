from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseCategory


# ── KnowledgeBase ──

async def get_list(
    db: AsyncSession, *, category_id: str | None = None, name: str = "",
) -> list[KnowledgeBase]:
    query = select(KnowledgeBase)
    if category_id:
        query = query.where(KnowledgeBase.category_id == category_id)
    if name:
        query = query.where(KnowledgeBase.name.ilike(f"%{name}%"))
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, kb_id: str) -> KnowledgeBase | None:
    return await db.get(KnowledgeBase, kb_id)


async def create(db: AsyncSession, *, name: str, description: str = "",
                 category_id: str | None = None, type: str = "public",
                 enabled: bool = True) -> KnowledgeBase:
    kb = KnowledgeBase(
        name=name, description=description,
        category_id=category_id, type=type, enabled=enabled,
    )
    db.add(kb)
    await db.commit()
    await db.refresh(kb)
    return kb


async def update(db: AsyncSession, kb: KnowledgeBase, *, name: str,
                 description: str = "", category_id: str | None = None,
                 type: str = "public", enabled: bool = True) -> KnowledgeBase:
    kb.name = name
    kb.description = description
    kb.category_id = category_id
    kb.type = type
    kb.enabled = enabled
    await db.commit()
    await db.refresh(kb)
    return kb


async def delete(db: AsyncSession, kb: KnowledgeBase) -> None:
    await db.delete(kb)
    await db.commit()


# ── Category ──

async def get_all_categories(db: AsyncSession) -> list[KnowledgeBaseCategory]:
    result = await db.execute(select(KnowledgeBaseCategory))
    return list(result.scalars().all())


async def get_category_by_id(db: AsyncSession, cat_id: str) -> KnowledgeBaseCategory | None:
    return await db.get(KnowledgeBaseCategory, cat_id)


async def create_category(db: AsyncSession, *, name: str,
                           parent_id: str | None = None) -> KnowledgeBaseCategory:
    cat = KnowledgeBaseCategory(name=name, parent_id=parent_id)
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


async def delete_category(db: AsyncSession, cat: KnowledgeBaseCategory) -> None:
    await db.delete(cat)
    await db.commit()
