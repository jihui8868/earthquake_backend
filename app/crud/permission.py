from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission


async def get_all(db: AsyncSession) -> list[Permission]:
    result = await db.execute(select(Permission))
    return list(result.scalars().all())


async def get_list(db: AsyncSession, keyword: str = "") -> list[Permission]:
    query = select(Permission)
    if keyword:
        query = query.where(Permission.name.ilike(f"%{keyword}%"))
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, perm_id: str) -> Permission | None:
    return await db.get(Permission, perm_id)


async def create(db: AsyncSession, *, name: str, code: str = "",
                 parent_id: str | None = None, type: str = "menu",
                 path: str = "", icon: str = "", sort: int = 0,
                 status: int = 1, remark: str = "") -> Permission:
    perm = Permission(
        name=name, code=code, parent_id=parent_id, type=type,
        path=path, icon=icon, sort=sort, status=status, remark=remark,
    )
    db.add(perm)
    await db.commit()
    await db.refresh(perm)
    return perm


async def update(db: AsyncSession, perm: Permission, *, name: str,
                 code: str = "", parent_id: str | None = None,
                 type: str = "menu", path: str = "", icon: str = "",
                 sort: int = 0, status: int = 1, remark: str = "") -> Permission:
    perm.name = name
    perm.code = code
    perm.parent_id = parent_id
    perm.type = type
    perm.path = path
    perm.icon = icon
    perm.sort = sort
    perm.status = status
    perm.remark = remark
    await db.commit()
    await db.refresh(perm)
    return perm


async def delete(db: AsyncSession, perm: Permission) -> None:
    await db.delete(perm)
    await db.commit()
