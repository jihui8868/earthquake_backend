import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.crud import file_system as crud
from app.models.file_system import FileItem
from app.schemas.common import ResponseModel
from app.schemas.file_system import FolderCreate, FileRename, FileMove, FileOut

router = APIRouter(prefix="/file-system", tags=["file-system"])


def _to_out(f: FileItem) -> FileOut:
    return FileOut(
        id=f.id, name=f.name, parentId=f.parent_id,
        isFolder=f.is_folder, size=f.size,
        createTime=f.created_at.isoformat() if f.created_at else "",
    )


def _build_tree(items: list[FileItem], parent_id: str | None = None) -> list[FileOut]:
    tree = []
    for item in items:
        if item.parent_id == parent_id:
            node = FileOut(
                id=item.id, name=item.name, parentId=item.parent_id,
                isFolder=item.is_folder, size=item.size,
                createTime=item.created_at.isoformat() if item.created_at else "",
                children=_build_tree(items, item.id) if item.is_folder else [],
            )
            tree.append(node)
    return tree


@router.get("/tree")
async def get_file_tree(db: AsyncSession = Depends(get_db)):
    items = await crud.get_all(db)
    tree = _build_tree(items)
    return ResponseModel(data=tree)


@router.get("/files")
async def get_files(parentId: str | None = None, db: AsyncSession = Depends(get_db)):
    items = await crud.get_by_parent(db, parent_id=parentId)
    return ResponseModel(data=[_to_out(f) for f in items])


@router.post("/folder")
async def create_folder(body: FolderCreate, db: AsyncSession = Depends(get_db)):
    folder = await crud.create_folder(db, name=body.name, parent_id=body.parentId)
    return ResponseModel(data=_to_out(folder))


@router.put("/files/{file_id}/rename")
async def rename_file(file_id: str, body: FileRename, db: AsyncSession = Depends(get_db)):
    item = await crud.get_by_id(db, file_id)
    if not item:
        return ResponseModel(code=404, message="文件不存在")
    item = await crud.rename(db, item, body.name)
    return ResponseModel(data=_to_out(item))


@router.delete("/files/{file_id}")
async def delete_file(file_id: str, db: AsyncSession = Depends(get_db)):
    item = await crud.get_by_id(db, file_id)
    if not item:
        return ResponseModel(code=404, message="文件不存在")
    if not item.is_folder and item.path and os.path.exists(item.path):
        os.remove(item.path)
    await crud.delete(db, item)
    return ResponseModel(message="删除成功")


@router.put("/files/{file_id}/move")
async def move_file(file_id: str, body: FileMove, db: AsyncSession = Depends(get_db)):
    item = await crud.get_by_id(db, file_id)
    if not item:
        return ResponseModel(code=404, message="文件不存在")
    item = await crud.move(db, item, body.targetParentId)
    return ResponseModel(data=_to_out(item))


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    parentId: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    upload_dir = os.path.join(settings.UPLOAD_DIR, "files")
    os.makedirs(upload_dir, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
    stored_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, stored_name)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    file_item = await crud.create_file(
        db, name=file.filename or stored_name,
        parent_id=parentId, size=len(content), path=file_path,
    )
    return ResponseModel(data=_to_out(file_item))


@router.get("/files/{file_id}/download")
async def download_file(file_id: str, db: AsyncSession = Depends(get_db)):
    item = await crud.get_by_id(db, file_id)
    if not item or not item.path or not os.path.exists(item.path):
        return ResponseModel(code=404, message="文件不存在")
    return FileResponse(path=item.path, filename=item.name)
