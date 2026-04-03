from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import knowledge_base as crud
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseCategory
from app.schemas.common import ResponseModel
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseOut,
    CategoryCreate, CategoryOut,
)

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


def _kb_to_out(kb: KnowledgeBase) -> KnowledgeBaseOut:
    return KnowledgeBaseOut(
        id=kb.id, name=kb.name, description=kb.description,
        categoryId=kb.category_id, type=kb.type, enabled=kb.enabled,
    )


def _build_category_tree(categories: list[KnowledgeBaseCategory], parent_id: str | None = None) -> list[CategoryOut]:
    tree = []
    for c in categories:
        if c.parent_id == parent_id:
            tree.append(CategoryOut(
                id=c.id, name=c.name, parentId=c.parent_id,
                count=len(c.knowledge_bases) if c.knowledge_bases else 0,
                children=_build_category_tree(categories, c.id),
            ))
    return tree


@router.get("/list")
async def get_knowledge_bases(
    page: int = 1, pageSize: int = 10, categoryId: str | None = None, name: str = "",
    db: AsyncSession = Depends(get_db),
):
    items = await crud.get_list(db, category_id=categoryId, name=name)
    return ResponseModel(data=[_kb_to_out(kb) for kb in items])


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    categories = await crud.get_all_categories(db)
    tree = _build_category_tree(categories)
    return ResponseModel(data=tree)


@router.post("/categories")
async def create_category(body: CategoryCreate, db: AsyncSession = Depends(get_db)):
    cat = await crud.create_category(db, name=body.name, parent_id=body.parentId)
    return ResponseModel(data=CategoryOut(id=cat.id, name=cat.name, parentId=cat.parent_id))


@router.delete("/categories/{cat_id}")
async def delete_category(cat_id: str, db: AsyncSession = Depends(get_db)):
    cat = await crud.get_category_by_id(db, cat_id)
    if not cat:
        return ResponseModel(code=404, message="分类不存在")
    await crud.delete_category(db, cat)
    return ResponseModel(message="删除成功")


@router.get("/{kb_id}")
async def get_knowledge_base(kb_id: str, db: AsyncSession = Depends(get_db)):
    kb = await crud.get_by_id(db, kb_id)
    if not kb:
        return ResponseModel(code=404, message="知识库不存在")
    return ResponseModel(data=_kb_to_out(kb))


@router.post("")
async def create_knowledge_base(body: KnowledgeBaseCreate, db: AsyncSession = Depends(get_db)):
    kb = await crud.create(
        db, name=body.name, description=body.description,
        category_id=body.categoryId, type=body.type, enabled=body.enabled,
    )
    return ResponseModel(data=_kb_to_out(kb))


@router.put("/{kb_id}")
async def update_knowledge_base(kb_id: str, body: KnowledgeBaseUpdate, db: AsyncSession = Depends(get_db)):
    kb = await crud.get_by_id(db, kb_id)
    if not kb:
        return ResponseModel(code=404, message="知识库不存在")
    kb = await crud.update(
        db, kb, name=body.name, description=body.description,
        category_id=body.categoryId, type=body.type, enabled=body.enabled,
    )
    return ResponseModel(data=_kb_to_out(kb))


@router.delete("/{kb_id}")
async def delete_knowledge_base(kb_id: str, db: AsyncSession = Depends(get_db)):
    kb = await crud.get_by_id(db, kb_id)
    if not kb:
        return ResponseModel(code=404, message="知识库不存在")
    await crud.delete(db, kb)
    return ResponseModel(message="删除成功")
