"""将前端权限 mock 数据插入到 PostgreSQL 数据库。"""

import asyncio
import uuid

from sqlalchemy import select

from app.core.database import engine, Base, async_session
from app.models.permission import Permission

MOCK_DATA = [
    {
        "id": "p1", "name": "地震数据", "code": "seismic", "type": "menu", "path": "/seismic", "sort": 1, "status": 1, "remark": "", "parentId": None,
        "children": [
            {"id": "p1-1", "name": "查看", "code": "seismic:view", "type": "button", "path": "", "sort": 1, "status": 1, "remark": "", "parentId": "p1", "children": []},
            {"id": "p1-2", "name": "上传", "code": "seismic:upload", "type": "button", "path": "", "sort": 2, "status": 1, "remark": "", "parentId": "p1", "children": []},
            {"id": "p1-3", "name": "删除", "code": "seismic:delete", "type": "button", "path": "", "sort": 3, "status": 1, "remark": "", "parentId": "p1", "children": []},
        ],
    },
    {
        "id": "p2", "name": "知识图谱", "code": "knowledge-graph", "type": "menu", "path": "/knowledge-graph", "sort": 2, "status": 1, "remark": "", "parentId": None,
        "children": [
            {"id": "p2-1", "name": "查看", "code": "kg:view", "type": "button", "path": "", "sort": 1, "status": 1, "remark": "", "parentId": "p2", "children": []},
            {"id": "p2-2", "name": "编辑", "code": "kg:edit", "type": "button", "path": "", "sort": 2, "status": 1, "remark": "", "parentId": "p2", "children": []},
        ],
    },
    {
        "id": "p3", "name": "系统管理", "code": "system", "type": "directory", "path": "/system", "sort": 5, "status": 1, "remark": "", "parentId": None,
        "children": [
            {
                "id": "p3-1", "name": "用户管理", "code": "system:user", "type": "menu", "path": "/system/user", "sort": 1, "status": 1, "remark": "", "parentId": "p3",
                "children": [
                    {"id": "p3-1-1", "name": "查看", "code": "system:user:view", "type": "button", "path": "", "sort": 1, "status": 1, "remark": "", "parentId": "p3-1", "children": []},
                    {"id": "p3-1-2", "name": "新增", "code": "system:user:add", "type": "button", "path": "", "sort": 2, "status": 1, "remark": "", "parentId": "p3-1", "children": []},
                    {"id": "p3-1-3", "name": "编辑", "code": "system:user:edit", "type": "button", "path": "", "sort": 3, "status": 1, "remark": "", "parentId": "p3-1", "children": []},
                    {"id": "p3-1-4", "name": "删除", "code": "system:user:delete", "type": "button", "path": "", "sort": 4, "status": 1, "remark": "", "parentId": "p3-1", "children": []},
                ],
            },
            {"id": "p3-2", "name": "角色管理", "code": "system:role", "type": "menu", "path": "/system/role", "sort": 2, "status": 1, "remark": "", "parentId": "p3", "children": []},
            {"id": "p3-3", "name": "部门管理", "code": "system:dept", "type": "menu", "path": "/system/department", "sort": 3, "status": 1, "remark": "", "parentId": "p3", "children": []},
        ],
    },
]


def _collect_ids(nodes, result=None):
    if result is None:
        result = []
    for node in nodes:
        result.append(node["id"])
        if node.get("children"):
            _collect_ids(node["children"], result)
    return result


def flatten(nodes, id_map, result=None):
    if result is None:
        result = []
    for node in nodes:
        old_id = node["id"]
        old_parent = node.get("parentId")
        result.append({
            "id": id_map[old_id],
            "name": node["name"],
            "code": node.get("code", ""),
            "parent_id": id_map[old_parent] if old_parent else None,
            "type": node.get("type", "menu"),
            "path": node.get("path", ""),
            "icon": node.get("icon", ""),
            "sort": node.get("sort", 0),
            "status": node.get("status", 1),
            "remark": node.get("remark", ""),
        })
        if node.get("children"):
            flatten(node["children"], id_map, result)
    return result


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    old_ids = _collect_ids(MOCK_DATA)
    id_map = {old_id: str(uuid.uuid4()) for old_id in old_ids}

    flat = flatten(MOCK_DATA, id_map)
    print(f"共 {len(flat)} 条权限数据")

    async with async_session() as db:
        existing = (await db.execute(select(Permission))).scalars().all()
        if existing:
            print(f"清空旧权限数据 {len(existing)} 条")
            for p in reversed(existing):
                await db.delete(p)
            await db.commit()

        for item in flat:
            db.add(Permission(**item))
        await db.commit()
        print(f"成功插入 {len(flat)} 条权限数据（UUID 主键）")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
