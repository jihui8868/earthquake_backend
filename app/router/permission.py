from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import permission as crud
from app.models.permission import Permission
from app.schemas.common import ResponseModel
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionOut

router = APIRouter(prefix="/system/permissions", tags=["permissions"])


def _build_tree(permissions: list[Permission], parent_id: str | None = None) -> list[PermissionOut]:
    tree = []
    for p in permissions:
        if p.parent_id == parent_id:
            node = PermissionOut(
                id=p.id, name=p.name, code=p.code, parentId=p.parent_id,
                type=p.type, path=p.path, icon=p.icon, sort=p.sort,
                status=p.status, remark=p.remark,
                children=_build_tree(permissions, p.id),
            )
            tree.append(node)
    tree.sort(key=lambda x: x.sort)
    return tree


def _to_out(p: Permission) -> PermissionOut:
    return PermissionOut(
        id=p.id, name=p.name, code=p.code, parentId=p.parent_id,
        type=p.type, path=p.path, icon=p.icon, sort=p.sort,
        status=p.status, remark=p.remark,
    )


@router.get("/tree")
async def get_permission_tree(db: AsyncSession = Depends(get_db)):
    permissions = await crud.get_all(db)
    tree = _build_tree(permissions)
    return ResponseModel(data=tree)


@router.get("")
async def get_permissions(
    page: int = 1, pageSize: int = 10, keyword: str = "",
    db: AsyncSession = Depends(get_db),
):
    all_items = await crud.get_list(db, keyword=keyword)
    total = len(all_items)
    start = (page - 1) * pageSize
    items = all_items[start : start + pageSize]
    return ResponseModel(data={"list": [_to_out(p) for p in items], "total": total})


@router.post("")
async def create_permission(body: PermissionCreate, db: AsyncSession = Depends(get_db)):
    perm = await crud.create(
        db, name=body.name, code=body.code, parent_id=body.parentId,
        type=body.type, path=body.path, icon=body.icon,
        sort=body.sort, status=body.status, remark=body.remark,
    )
    return ResponseModel(data=_to_out(perm))


@router.put("/{perm_id}")
async def update_permission(perm_id: str, body: PermissionUpdate, db: AsyncSession = Depends(get_db)):
    perm = await crud.get_by_id(db, perm_id)
    if not perm:
        return ResponseModel(code=404, message="权限不存在")
    perm = await crud.update(
        db, perm, name=body.name, code=body.code, parent_id=body.parentId,
        type=body.type, path=body.path, icon=body.icon,
        sort=body.sort, status=body.status, remark=body.remark,
    )
    return ResponseModel(data=_to_out(perm))


@router.delete("/{perm_id}")
async def delete_permission(perm_id: str, db: AsyncSession = Depends(get_db)):
    perm = await crud.get_by_id(db, perm_id)
    if not perm:
        return ResponseModel(code=404, message="权限不存在")
    await crud.delete(db, perm)
    return ResponseModel(message="删除成功")
