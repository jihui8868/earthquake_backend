import json
import os

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.crud import knowledge_graph as crud
from app.models.knowledge_graph import KnowledgeGraphFile, KnowledgeGraphNode, KnowledgeGraphRelation
from app.schemas.common import ResponseModel
from app.schemas.knowledge_graph import KGFileOut, KGNodeOut, KGRelationOut, GraphData, GraphStats

router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])


def _file_to_out(f: KnowledgeGraphFile) -> KGFileOut:
    return KGFileOut(
        id=f.id, name=f.name, size=f.size, status=f.status,
        createTime=f.created_at.isoformat() if f.created_at else "",
    )


def _node_to_out(n: KnowledgeGraphNode) -> KGNodeOut:
    props = {}
    if n.properties:
        try:
            props = json.loads(n.properties)
        except (json.JSONDecodeError, TypeError):
            pass
    return KGNodeOut(id=n.id, name=n.name, type=n.type, weight=n.weight, properties=props)


def _relation_to_out(r: KnowledgeGraphRelation) -> KGRelationOut:
    return KGRelationOut(id=r.id, sourceId=r.source_id, targetId=r.target_id, type=r.type)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    upload_dir = os.path.join(settings.UPLOAD_DIR, "knowledge_graph")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    kg_file = await crud.create_file(db, name=file.filename, path=file_path, size=len(content))
    return ResponseModel(data=_file_to_out(kg_file))


@router.get("/files")
async def get_files(page: int = 1, pageSize: int = 10, db: AsyncSession = Depends(get_db)):
    files = await crud.get_all_files(db)
    return ResponseModel(data=[_file_to_out(f) for f in files])


@router.delete("/files/{file_id}")
async def delete_file(file_id: str, db: AsyncSession = Depends(get_db)):
    kg_file = await crud.get_file_by_id(db, file_id)
    if not kg_file:
        return ResponseModel(code=404, message="文件不存在")
    if kg_file.path and os.path.exists(kg_file.path):
        os.remove(kg_file.path)
    await crud.delete_file(db, kg_file)
    return ResponseModel(message="删除成功")


@router.post("/files/{file_id}/parse")
async def parse_file(file_id: str, db: AsyncSession = Depends(get_db)):
    kg_file = await crud.get_file_by_id(db, file_id)
    if not kg_file:
        return ResponseModel(code=404, message="文件不存在")
    await crud.update_file_status(db, kg_file, "parsing")
    # TODO: implement actual parsing logic
    kg_file = await crud.update_file_status(db, kg_file, "completed")
    return ResponseModel(data=_file_to_out(kg_file))


@router.get("/files/{file_id}/parse-status")
async def get_parse_status(file_id: str, db: AsyncSession = Depends(get_db)):
    kg_file = await crud.get_file_by_id(db, file_id)
    if not kg_file:
        return ResponseModel(code=404, message="文件不存在")
    return ResponseModel(data={"status": kg_file.status})


@router.get("/graph")
async def get_graph(db: AsyncSession = Depends(get_db)):
    nodes = [_node_to_out(n) for n in await crud.get_all_nodes(db)]
    relations = [_relation_to_out(r) for r in await crud.get_all_relations(db)]
    return ResponseModel(data=GraphData(nodes=nodes, relations=relations))


@router.get("/nodes/search")
async def search_nodes(keyword: str = "", db: AsyncSession = Depends(get_db)):
    nodes = [_node_to_out(n) for n in await crud.search_nodes(db, keyword=keyword)]
    return ResponseModel(data=nodes)


@router.get("/nodes/{node_id}")
async def get_node(node_id: str, db: AsyncSession = Depends(get_db)):
    node = await crud.get_node_by_id(db, node_id)
    if not node:
        return ResponseModel(code=404, message="节点不存在")
    return ResponseModel(data=_node_to_out(node))


@router.get("/nodes/{node_id}/relations")
async def get_node_relations(node_id: str, db: AsyncSession = Depends(get_db)):
    relations = [_relation_to_out(r) for r in await crud.get_node_relations(db, node_id)]
    return ResponseModel(data=relations)


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    stats = await crud.get_stats(db)
    return ResponseModel(data=GraphStats(**stats))
