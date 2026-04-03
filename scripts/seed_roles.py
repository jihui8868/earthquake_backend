"""将前端角色 mock 数据插入到 PostgreSQL 数据库。"""

import asyncio
import uuid

from sqlalchemy import select

from app.core.database import engine, Base, async_session
from app.models.role import Role

MOCK_ROLES = [
    {"name": "超级管理员", "code": "admin", "sort": 1, "status": 1, "remark": "拥有所有权限"},
    {"name": "普通用户", "code": "user", "sort": 2, "status": 1, "remark": "基础权限"},
    {"name": "开发人员", "code": "developer", "sort": 3, "status": 1, "remark": "开发相关权限"},
    {"name": "数据分析师", "code": "analyst", "sort": 4, "status": 1, "remark": "数据查看权限"},
    {"name": "访客", "code": "guest", "sort": 5, "status": 0, "remark": "只读权限"},
]


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        existing = (await db.execute(select(Role))).scalars().all()
        if existing:
            print(f"清空旧角色数据 {len(existing)} 条")
            for r in existing:
                await db.delete(r)
            await db.commit()

        for item in MOCK_ROLES:
            db.add(Role(id=str(uuid.uuid4()), **item))
        await db.commit()
        print(f"成功插入 {len(MOCK_ROLES)} 条角色数据（UUID 主键）")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
