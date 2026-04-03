from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import user as crud
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.user import UserCreate, UserUpdate, UserOut

router = APIRouter(prefix="/system/users", tags=["users"])


def _to_out(u: User) -> UserOut:
    return UserOut(
        id=u.id, username=u.username, nickname=u.nickname,
        email=u.email, phone=u.phone, deptId=u.dept_id,
        deptName=u.department.name if u.department else "",
        roleId=u.role_id,
        roleName=u.role.name if u.role else "",
        status=u.status, remark=u.remark,
    )


@router.get("")
async def get_users(
    page: int = 1, pageSize: int = 10, keyword: str = "",
    status: int | None = None, deptId: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    users, total = await crud.get_list(
        db, page=page, page_size=pageSize,
        keyword=keyword, status=status, dept_id=deptId,
    )
    return ResponseModel(data={"list": [_to_out(u) for u in users], "total": total})


@router.get("/{user_id}")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_by_id(db, user_id)
    if not user:
        return ResponseModel(code=404, message="用户不存在")
    return ResponseModel(data=_to_out(user))


@router.post("")
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await crud.create(
        db, username=body.username, nickname=body.nickname, email=body.email,
        phone=body.phone, dept_id=body.deptId, role_id=body.roleId,
        status=body.status, remark=body.remark,
    )
    return ResponseModel(data=_to_out(user))


@router.put("/{user_id}")
async def update_user(user_id: str, body: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await crud.get_by_id(db, user_id)
    if not user:
        return ResponseModel(code=404, message="用户不存在")
    user = await crud.update(
        db, user, username=body.username, nickname=body.nickname, email=body.email,
        phone=body.phone, dept_id=body.deptId, role_id=body.roleId,
        status=body.status, remark=body.remark,
    )
    return ResponseModel(data=_to_out(user))


@router.delete("/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_by_id(db, user_id)
    if not user:
        return ResponseModel(code=404, message="用户不存在")
    await crud.delete(db, user)
    return ResponseModel(message="删除成功")


@router.put("/{user_id}/reset-password")
async def reset_password(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_by_id(db, user_id)
    if not user:
        return ResponseModel(code=404, message="用户不存在")
    await crud.reset_password(db, user)
    return ResponseModel(message="密码重置成功")
