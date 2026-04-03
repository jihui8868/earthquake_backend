from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_graph import KnowledgeGraphFile, KnowledgeGraphNode, KnowledgeGraphRelation


# ── File ──

async def create_file(db: AsyncSession, *, name: str, path: str,
                      size: int, status: str = "pending") -> KnowledgeGraphFile:
    kg_file = KnowledgeGraphFile(name=name, path=path, size=size, status=status)
    db.add(kg_file)
    await db.commit()
    await db.refresh(kg_file)
    return kg_file


async def get_all_files(db: AsyncSession) -> list[KnowledgeGraphFile]:
    result = await db.execute(
        select(KnowledgeGraphFile).order_by(KnowledgeGraphFile.created_at.desc())
    )
    return list(result.scalars().all())


async def get_file_by_id(db: AsyncSession, file_id: str) -> KnowledgeGraphFile | None:
    return await db.get(KnowledgeGraphFile, file_id)


async def update_file_status(db: AsyncSession, kg_file: KnowledgeGraphFile,
                              status: str) -> KnowledgeGraphFile:
    kg_file.status = status
    await db.commit()
    await db.refresh(kg_file)
    return kg_file


async def delete_file(db: AsyncSession, kg_file: KnowledgeGraphFile) -> None:
    await db.delete(kg_file)
    await db.commit()


# ── Node ──

async def get_all_nodes(db: AsyncSession) -> list[KnowledgeGraphNode]:
    result = await db.execute(select(KnowledgeGraphNode))
    return list(result.scalars().all())


async def search_nodes(db: AsyncSession, keyword: str = "") -> list[KnowledgeGraphNode]:
    query = select(KnowledgeGraphNode)
    if keyword:
        query = query.where(KnowledgeGraphNode.name.ilike(f"%{keyword}%"))
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_node_by_id(db: AsyncSession, node_id: str) -> KnowledgeGraphNode | None:
    return await db.get(KnowledgeGraphNode, node_id)


# ── Relation ──

async def get_all_relations(db: AsyncSession) -> list[KnowledgeGraphRelation]:
    result = await db.execute(select(KnowledgeGraphRelation))
    return list(result.scalars().all())


async def get_node_relations(db: AsyncSession, node_id: str) -> list[KnowledgeGraphRelation]:
    result = await db.execute(
        select(KnowledgeGraphRelation).where(
            (KnowledgeGraphRelation.source_id == node_id)
            | (KnowledgeGraphRelation.target_id == node_id)
        )
    )
    return list(result.scalars().all())


# ── Stats ──

async def get_stats(db: AsyncSession) -> dict[str, int]:
    node_count = (await db.execute(select(sa_func.count()).select_from(KnowledgeGraphNode))).scalar() or 0
    relation_count = (await db.execute(select(sa_func.count()).select_from(KnowledgeGraphRelation))).scalar() or 0
    file_count = (await db.execute(select(sa_func.count()).select_from(KnowledgeGraphFile))).scalar() or 0
    return {"nodeCount": node_count, "relationCount": relation_count, "fileCount": file_count}
