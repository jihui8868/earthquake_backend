from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import role as crud
from app.models.role import Role
from app.schemas.common import ResponseModel
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut, RolePermissionUpdate

router = APIRouter(prefix="/system/roles", tags=["roles"])


def _to_out(r: Role) -> RoleOut:
    return RoleOut(id=r.id, name=r.name, code=r.code, sort=r.sort, status=r.status, remark=r.remark)


@router.get("")
async def get_roles(
    page: int = 1, pageSize: int = 10, keyword: str = "",
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    roles, total = await crud.get_list(
        db, page=page, page_size=pageSize, keyword=keyword, status=status,
    )
    return ResponseModel(data={"list": [_to_out(r) for r in roles], "total": total})


@router.get("/{role_id}")
async def get_role(role_id: str, db: AsyncSession = Depends(get_db)):
    role = await crud.get_by_id(db, role_id)
    if not role:
        return ResponseModel(code=404, message="角色不存在")
    return ResponseModel(data=_to_out(role))


@router.post("")
async def create_role(body: RoleCreate, db: AsyncSession = Depends(get_db)):
    role = await crud.create(
        db, name=body.name, code=body.code, sort=body.sort,
        status=body.status, remark=body.remark,
    )
    return ResponseModel(data=_to_out(role))


@router.put("/{role_id}")
async def update_role(role_id: str, body: RoleUpdate, db: AsyncSession = Depends(get_db)):
    role = await crud.get_by_id(db, role_id)
    if not role:
        return ResponseModel(code=404, message="角色不存在")
    role = await crud.update(
        db, role, name=body.name, code=body.code, sort=body.sort,
        status=body.status, remark=body.remark,
    )
    return ResponseModel(data=_to_out(role))


@router.delete("/{role_id}")
async def delete_role(role_id: str, db: AsyncSession = Depends(get_db)):
    role = await crud.get_by_id(db, role_id)
    if not role:
        return ResponseModel(code=404, message="角色不存在")
    await crud.delete(db, role)
    return ResponseModel(message="删除成功")


@router.get("/{role_id}/permissions")
async def get_role_permissions(role_id: str, db: AsyncSession = Depends(get_db)):
    permission_ids = await crud.get_permission_ids(db, role_id)
    return ResponseModel(data=permission_ids)


@router.put("/{role_id}/permissions")
async def update_role_permissions(role_id: str, body: RolePermissionUpdate, db: AsyncSession = Depends(get_db)):
    await crud.update_permissions(db, role_id, body.permissionIds)
    return ResponseModel(message="权限更新成功")
