"""将前端用户 mock 数据插入到 PostgreSQL 数据库，deptId 通过部门名称匹配为 UUID。"""

import asyncio
import uuid

from sqlalchemy import select

from app.core.database import engine, Base, async_session
from app.models.department import Department
from app.models.user import User

# 前端 User.vue 中的 mockUsers，deptName 用于匹配数据库中的部门
MOCK_USERS = [
    {"username": "admin", "nickname": "戴厚良", "email": "dai@cnpc.com.cn", "phone": "010-59986000", "deptName": "中国石油天然气集团有限公司", "roleName": "超级管理员", "status": 1},
    {"username": "lvdongfang", "nickname": "吕东方", "email": "lv@bgp.com.cn", "phone": "010-81706000", "deptName": "东方地球物理公司", "roleName": "部门管理员", "status": 1},
    {"username": "shiyan", "nickname": "施研", "email": "shi@bgp.com.cn", "phone": "010-81706001", "deptName": "研究院", "roleName": "开发人员", "status": 1, "deptLeader": "施研"},
    {"username": "huawu", "nickname": "华物", "email": "hua@riped.cn", "phone": "010-83596001", "deptName": "地球物理研究所", "roleName": "数据分析师", "status": 1},
    {"username": "liutan", "nickname": "刘探", "email": "liu@daqing.cnpc.com.cn", "phone": "0459-5991004", "deptName": "物探公司", "roleName": "普通用户", "status": 1},
    {"username": "zhaoyuan", "nickname": "赵院", "email": "zhao@changqing.cnpc.com.cn", "phone": "029-86591001", "deptName": "勘探开发研究院", "roleName": "普通用户", "status": 1, "deptLeader": "赵院"},
    {"username": "taofeichang", "nickname": "陶非", "email": "tao@riped.cn", "phone": "010-83596004", "deptName": "非常规研究所", "roleName": "开发人员", "status": 1},
    {"username": "yangtali", "nickname": "杨塔", "email": "yang@tarim.cnpc.com.cn", "phone": "0996-2091000", "deptName": "塔里木油田分公司", "roleName": "部门管理员", "status": 1},
    {"username": "zhengxi", "nickname": "郑西", "email": "zheng@swog.cnpc.com.cn", "phone": "028-86011000", "deptName": "西南油气田分公司", "roleName": "部门管理员", "status": 0},
    {"username": "zhaogang", "nickname": "赵刚", "email": "zhaogang@cnpc.com.cn", "phone": "010-59986004", "deptName": "科技与信息化部", "roleName": "部门管理员", "status": 1},
]

# 用 leader 字段精确匹配部门（解决同名部门问题）
# 前端中多个子公司都有 "勘探开发研究院"，通过 leader 区分
LEADER_MATCH = {
    "shiyan": "施研",     # 东方地球物理公司/研究院
    "zhaoyuan": "赵院",   # 长庆油田/勘探开发研究院
}


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # 加载所有部门，建立 name->id 和 leader->dept 映射
        depts = (await db.execute(select(Department))).scalars().all()
        name_to_depts: dict[str, list[Department]] = {}
        for d in depts:
            name_to_depts.setdefault(d.name, []).append(d)

        # 清空旧用户
        existing = (await db.execute(select(User))).scalars().all()
        if existing:
            print(f"清空旧用户数据 {len(existing)} 条")
            for u in existing:
                await db.delete(u)
            await db.commit()

        count = 0
        for u in MOCK_USERS:
            dept_name = u["deptName"]
            dept_id = None
            candidates = name_to_depts.get(dept_name, [])
            if len(candidates) == 1:
                dept_id = candidates[0].id
            elif len(candidates) > 1:
                # 多个同名部门，用 leader 精确匹配
                leader = LEADER_MATCH.get(u["username"])
                if leader:
                    for c in candidates:
                        if c.leader == leader:
                            dept_id = c.id
                            break
                if not dept_id:
                    dept_id = candidates[0].id

            if not dept_id:
                print(f"  警告: 用户 {u['username']} 的部门 '{dept_name}' 未找到，dept_id 为空")

            user = User(
                id=str(uuid.uuid4()),
                username=u["username"],
                nickname=u["nickname"],
                email=u["email"],
                phone=u["phone"],
                dept_id=dept_id,
                status=u["status"],
            )
            db.add(user)
            count += 1

        await db.commit()
        print(f"成功插入 {count} 条用户数据（UUID 主键）")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
