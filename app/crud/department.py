from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department


async def get_all(db: AsyncSession) -> list[Department]:
    result = await db.execute(select(Department))
    return list(result.scalars().all())


async def get_list(db: AsyncSession, keyword: str = "") -> list[Department]:
    query = select(Department)
    if keyword:
        query = query.where(Department.name.ilike(f"%{keyword}%"))
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, dept_id: str) -> Department | None:
    return await db.get(Department, dept_id)


async def create(db: AsyncSession, *, name: str, parent_id: str | None = None,
                 sort: int = 0, leader: str = "", phone: str = "",
                 status: int = 1, remark: str = "") -> Department:
    dept = Department(
        name=name, parent_id=parent_id, sort=sort,
        leader=leader, phone=phone, status=status, remark=remark,
    )
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


async def update(db: AsyncSession, dept: Department, *, name: str,
                 parent_id: str | None = None, sort: int = 0,
                 leader: str = "", phone: str = "", status: int = 1,
                 remark: str = "") -> Department:
    dept.name = name
    dept.parent_id = parent_id
    dept.sort = sort
    dept.leader = leader
    dept.phone = phone
    dept.status = status
    dept.remark = remark
    await db.commit()
    await db.refresh(dept)
    return dept


async def delete(db: AsyncSession, dept: Department) -> None:
    await db.delete(dept)
    await db.commit()
