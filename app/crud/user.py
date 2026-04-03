from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_list(
    db: AsyncSession, *, page: int = 1, page_size: int = 10,
    keyword: str = "", status: int | None = None, dept_id: str | None = None,
) -> tuple[list[User], int]:
    query = select(User)
    count_query = select(sa_func.count()).select_from(User)

    if keyword:
        cond = User.username.ilike(f"%{keyword}%") | User.nickname.ilike(f"%{keyword}%")
        query = query.where(cond)
        count_query = count_query.where(cond)
    if status is not None:
        query = query.where(User.status == status)
        count_query = count_query.where(User.status == status)
    if dept_id:
        query = query.where(User.dept_id == dept_id)
        count_query = count_query.where(User.dept_id == dept_id)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_by_id(db: AsyncSession, user_id: str) -> User | None:
    return await db.get(User, user_id)


async def create(db: AsyncSession, *, username: str, nickname: str = "",
                 email: str = "", phone: str = "", dept_id: str | None = None,
                 role_id: str | None = None, status: int = 1,
                 remark: str = "") -> User:
    user = User(
        username=username, nickname=nickname, email=email,
        phone=phone, dept_id=dept_id, role_id=role_id,
        status=status, remark=remark,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update(db: AsyncSession, user: User, *, username: str,
                 nickname: str = "", email: str = "", phone: str = "",
                 dept_id: str | None = None, role_id: str | None = None,
                 status: int = 1, remark: str = "") -> User:
    user.username = username
    user.nickname = nickname
    user.email = email
    user.phone = phone
    user.dept_id = dept_id
    user.role_id = role_id
    user.status = status
    user.remark = remark
    await db.commit()
    await db.refresh(user)
    return user


async def delete(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()


async def reset_password(db: AsyncSession, user: User) -> None:
    user.password = "123456"
    await db.commit()
