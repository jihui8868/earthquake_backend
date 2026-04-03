from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role, RolePermission


async def get_list(
    db: AsyncSession, *, page: int = 1, page_size: int = 10,
    keyword: str = "", status: int | None = None,
) -> tuple[list[Role], int]:
    query = select(Role)
    count_query = select(sa_func.count()).select_from(Role)

    if keyword:
        cond = Role.name.ilike(f"%{keyword}%") | Role.code.ilike(f"%{keyword}%")
        query = query.where(cond)
        count_query = count_query.where(cond)
    if status is not None:
        query = query.where(Role.status == status)
        count_query = count_query.where(Role.status == status)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(Role.sort).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_by_id(db: AsyncSession, role_id: str) -> Role | None:
    return await db.get(Role, role_id)


async def create(db: AsyncSession, *, name: str, code: str,
                 sort: int = 0, status: int = 1, remark: str = "") -> Role:
    role = Role(name=name, code=code, sort=sort, status=status, remark=remark)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def update(db: AsyncSession, role: Role, *, name: str, code: str,
                 sort: int = 0, status: int = 1, remark: str = "") -> Role:
    role.name = name
    role.code = code
    role.sort = sort
    role.status = status
    role.remark = remark
    await db.commit()
    await db.refresh(role)
    return role


async def delete(db: AsyncSession, role: Role) -> None:
    await db.delete(role)
    await db.commit()


async def get_permission_ids(db: AsyncSession, role_id: str) -> list[str]:
    result = await db.execute(
        select(RolePermission.permission_id).where(RolePermission.role_id == role_id)
    )
    return [row[0] for row in result.all()]


async def update_permissions(db: AsyncSession, role_id: str, permission_ids: list[str]) -> None:
    existing = await db.execute(
        select(RolePermission).where(RolePermission.role_id == role_id)
    )
    for rp in existing.scalars().all():
        await db.delete(rp)
    for pid in permission_ids:
        db.add(RolePermission(role_id=role_id, permission_id=pid))
    await db.commit()
