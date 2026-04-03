"""将前端部门 mock 数据插入到 PostgreSQL 数据库。"""

import asyncio
import uuid

from sqlalchemy import select

from app.core.database import engine, Base, async_session
from app.models.department import Department

MOCK_DATA = [
    {
        "id": "1", "name": "中国石油天然气集团有限公司", "parentId": None, "sort": 1, "leader": "戴厚良", "phone": "010-59986000", "status": 1, "remark": "集团总部",
        "children": [
            {"id": "1-1", "name": "办公厅", "parentId": "1", "sort": 1, "leader": "王明", "phone": "010-59986001", "status": 1, "remark": "", "children": []},
            {"id": "1-2", "name": "人力资源部", "parentId": "1", "sort": 2, "leader": "李强", "phone": "010-59986002", "status": 1, "remark": "", "children": []},
            {"id": "1-3", "name": "财务部", "parentId": "1", "sort": 3, "leader": "张丽", "phone": "010-59986003", "status": 1, "remark": "", "children": []},
            {
                "id": "1-4", "name": "科技与信息化部", "parentId": "1", "sort": 4, "leader": "赵刚", "phone": "010-59986004", "status": 1, "remark": "",
                "children": [
                    {"id": "1-4-1", "name": "科技管理处", "parentId": "1-4", "sort": 1, "leader": "孙科", "phone": "010-59986041", "status": 1, "remark": "", "children": []},
                    {"id": "1-4-2", "name": "信息化管理处", "parentId": "1-4", "sort": 2, "leader": "周信", "phone": "010-59986042", "status": 1, "remark": "", "children": []},
                    {"id": "1-4-3", "name": "数字化转型处", "parentId": "1-4", "sort": 3, "leader": "吴数", "phone": "010-59986043", "status": 1, "remark": "", "children": []},
                ],
            },
            {"id": "1-5", "name": "安全环保与节能部", "parentId": "1", "sort": 5, "leader": "刘安", "phone": "010-59986005", "status": 1, "remark": "", "children": []},
            {"id": "1-6", "name": "规划计划部", "parentId": "1", "sort": 6, "leader": "陈规", "phone": "010-59986006", "status": 1, "remark": "", "children": []},
            {
                "id": "1-10", "name": "勘探与生产分公司", "parentId": "1", "sort": 10, "leader": "黄勘", "phone": "010-59986010", "status": 1, "remark": "上游核心业务",
                "children": [
                    {
                        "id": "1-10-1", "name": "大庆油田有限责任公司", "parentId": "1-10", "sort": 1, "leader": "朱国文", "phone": "0459-5991000", "status": 1, "remark": "中国最大油田",
                        "children": [
                            {"id": "1-10-1-1", "name": "勘探开发研究院", "parentId": "1-10-1", "sort": 1, "leader": "王院", "phone": "0459-5991001", "status": 1, "remark": "", "children": []},
                            {"id": "1-10-1-2", "name": "采油一厂", "parentId": "1-10-1", "sort": 2, "leader": "李采", "phone": "0459-5991002", "status": 1, "remark": "", "children": []},
                            {"id": "1-10-1-3", "name": "采油二厂", "parentId": "1-10-1", "sort": 3, "leader": "张采", "phone": "0459-5991003", "status": 1, "remark": "", "children": []},
                            {"id": "1-10-1-4", "name": "物探公司", "parentId": "1-10-1", "sort": 4, "leader": "刘探", "phone": "0459-5991004", "status": 1, "remark": "地震勘探作业", "children": []},
                        ],
                    },
                    {
                        "id": "1-10-2", "name": "长庆油田分公司", "parentId": "1-10", "sort": 2, "leader": "何军", "phone": "029-86591000", "status": 1, "remark": "国内产量最高油气田",
                        "children": [
                            {"id": "1-10-2-1", "name": "勘探开发研究院", "parentId": "1-10-2", "sort": 1, "leader": "赵院", "phone": "029-86591001", "status": 1, "remark": "", "children": []},
                            {"id": "1-10-2-2", "name": "第一采油厂", "parentId": "1-10-2", "sort": 2, "leader": "钱采", "phone": "029-86591002", "status": 1, "remark": "", "children": []},
                            {"id": "1-10-2-3", "name": "第一采气厂", "parentId": "1-10-2", "sort": 3, "leader": "孙气", "phone": "029-86591003", "status": 1, "remark": "", "children": []},
                        ],
                    },
                    {
                        "id": "1-10-3", "name": "塔里木油田分公司", "parentId": "1-10", "sort": 3, "leader": "杨塔", "phone": "0996-2091000", "status": 1, "remark": "西气东输主力气源地",
                        "children": [
                            {"id": "1-10-3-1", "name": "勘探开发研究院", "parentId": "1-10-3", "sort": 1, "leader": "周院", "phone": "0996-2091001", "status": 1, "remark": "", "children": []},
                            {"id": "1-10-3-2", "name": "博孜-大北作业区", "parentId": "1-10-3", "sort": 2, "leader": "吴区", "phone": "0996-2091002", "status": 1, "remark": "", "children": []},
                        ],
                    },
                    {
                        "id": "1-10-4", "name": "西南油气田分公司", "parentId": "1-10", "sort": 4, "leader": "郑西", "phone": "028-86011000", "status": 1, "remark": "四川盆地天然气开发",
                        "children": [
                            {"id": "1-10-4-1", "name": "勘探开发研究院", "parentId": "1-10-4", "sort": 1, "leader": "冯院", "phone": "028-86011001", "status": 1, "remark": "", "children": []},
                            {"id": "1-10-4-2", "name": "蜀南气矿", "parentId": "1-10-4", "sort": 2, "leader": "褚矿", "phone": "028-86011002", "status": 1, "remark": "", "children": []},
                        ],
                    },
                    {"id": "1-10-5", "name": "新疆油田分公司", "parentId": "1-10", "sort": 5, "leader": "卫新", "phone": "0990-6681000", "status": 1, "remark": "准噶尔盆地", "children": []},
                    {"id": "1-10-6", "name": "辽河油田分公司", "parentId": "1-10", "sort": 6, "leader": "蒋辽", "phone": "0427-7281000", "status": 1, "remark": "稠油开发", "children": []},
                    {"id": "1-10-7", "name": "吉林油田分公司", "parentId": "1-10", "sort": 7, "leader": "沈吉", "phone": "0438-6201000", "status": 1, "remark": "", "children": []},
                ],
            },
            {
                "id": "1-20", "name": "炼油化工和新材料分公司", "parentId": "1", "sort": 20, "leader": "韩炼", "phone": "010-59986020", "status": 1, "remark": "中下游业务",
                "children": [
                    {"id": "1-20-1", "name": "大连石化公司", "parentId": "1-20", "sort": 1, "leader": "秦大", "phone": "0411-8361000", "status": 1, "remark": "", "children": []},
                    {"id": "1-20-2", "name": "兰州石化公司", "parentId": "1-20", "sort": 2, "leader": "尤兰", "phone": "0931-7961000", "status": 1, "remark": "", "children": []},
                    {"id": "1-20-3", "name": "独山子石化公司", "parentId": "1-20", "sort": 3, "leader": "许独", "phone": "0992-3681000", "status": 1, "remark": "", "children": []},
                ],
            },
            {
                "id": "1-30", "name": "工程技术分公司", "parentId": "1", "sort": 30, "leader": "何工", "phone": "010-59986030", "status": 1, "remark": "",
                "children": [
                    {
                        "id": "1-30-1", "name": "东方地球物理公司", "parentId": "1-30", "sort": 1, "leader": "吕东方", "phone": "010-81706000", "status": 1, "remark": "全球最大地震勘探公司",
                        "children": [
                            {"id": "1-30-1-1", "name": "研究院", "parentId": "1-30-1", "sort": 1, "leader": "施研", "phone": "010-81706001", "status": 1, "remark": "地震资料处理解释", "children": []},
                            {"id": "1-30-1-2", "name": "装备制造中心", "parentId": "1-30-1", "sort": 2, "leader": "张装", "phone": "010-81706002", "status": 1, "remark": "地震仪器研发", "children": []},
                            {"id": "1-30-1-3", "name": "国际业务部", "parentId": "1-30-1", "sort": 3, "leader": "王国", "phone": "010-81706003", "status": 1, "remark": "", "children": []},
                        ],
                    },
                    {"id": "1-30-2", "name": "长城钻探工程公司", "parentId": "1-30", "sort": 2, "leader": "孟长", "phone": "010-59986031", "status": 1, "remark": "钻完井工程", "children": []},
                    {"id": "1-30-3", "name": "渤海钻探工程公司", "parentId": "1-30", "sort": 3, "leader": "苏渤", "phone": "022-66291000", "status": 1, "remark": "", "children": []},
                ],
            },
            {
                "id": "1-40", "name": "科技研究板块", "parentId": "1", "sort": 40, "leader": "曹科", "phone": "010-59986040", "status": 1, "remark": "",
                "children": [
                    {
                        "id": "1-40-1", "name": "勘探开发研究院", "parentId": "1-40", "sort": 1, "leader": "严勘", "phone": "010-83596000", "status": 1, "remark": "油气勘探开发核心研究院",
                        "children": [
                            {"id": "1-40-1-1", "name": "地球物理研究所", "parentId": "1-40-1", "sort": 1, "leader": "华物", "phone": "010-83596001", "status": 1, "remark": "地震方法研究", "children": []},
                            {"id": "1-40-1-2", "name": "地质研究所", "parentId": "1-40-1", "sort": 2, "leader": "金地", "phone": "010-83596002", "status": 1, "remark": "", "children": []},
                            {"id": "1-40-1-3", "name": "开发研究所", "parentId": "1-40-1", "sort": 3, "leader": "魏开", "phone": "010-83596003", "status": 1, "remark": "", "children": []},
                            {"id": "1-40-1-4", "name": "非常规研究所", "parentId": "1-40-1", "sort": 4, "leader": "陶非", "phone": "010-83596004", "status": 1, "remark": "页岩油气研究", "children": []},
                        ],
                    },
                    {"id": "1-40-2", "name": "石油化工研究院", "parentId": "1-40", "sort": 2, "leader": "姜化", "phone": "010-82311000", "status": 1, "remark": "", "children": []},
                    {"id": "1-40-3", "name": "工程技术研究院", "parentId": "1-40", "sort": 3, "leader": "齐工", "phone": "010-82311500", "status": 1, "remark": "钻完井与地面工程研究", "children": []},
                ],
            },
            {
                "id": "1-50", "name": "销售分公司", "parentId": "1", "sort": 50, "leader": "谢销", "phone": "010-59986050", "status": 1, "remark": "成品油与天然气销售",
                "children": [
                    {"id": "1-50-1", "name": "华北销售公司", "parentId": "1-50", "sort": 1, "leader": "邹北", "phone": "010-59986051", "status": 1, "remark": "", "children": []},
                    {"id": "1-50-2", "name": "华东销售公司", "parentId": "1-50", "sort": 2, "leader": "喻东", "phone": "021-52071000", "status": 1, "remark": "", "children": []},
                    {"id": "1-50-3", "name": "西南销售公司", "parentId": "1-50", "sort": 3, "leader": "柏西", "phone": "028-86011500", "status": 1, "remark": "", "children": []},
                ],
            },
        ],
    },
]


def _collect_ids(nodes: list[dict], result: list[str] | None = None) -> list[str]:
    """递归收集所有旧 id。"""
    if result is None:
        result = []
    for node in nodes:
        result.append(node["id"])
        if node.get("children"):
            _collect_ids(node["children"], result)
    return result


def flatten(nodes: list[dict], id_map: dict[str, str],
            result: list[dict] | None = None) -> list[dict]:
    """将树形数据展平，使用 id_map 将旧 id 替换为 UUID。"""
    if result is None:
        result = []
    for node in nodes:
        old_id = node["id"]
        old_parent = node.get("parentId")
        result.append({
            "id": id_map[old_id],
            "name": node["name"],
            "parent_id": id_map[old_parent] if old_parent else None,
            "sort": node.get("sort", 0),
            "leader": node.get("leader", ""),
            "phone": node.get("phone", ""),
            "status": node.get("status", 1),
            "remark": node.get("remark", ""),
        })
        if node.get("children"):
            flatten(node["children"], id_map, result)
    return result


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 为每个旧 id 生成 UUID
    old_ids = _collect_ids(MOCK_DATA)
    id_map = {old_id: str(uuid.uuid4()) for old_id in old_ids}

    flat = flatten(MOCK_DATA, id_map)
    print(f"共 {len(flat)} 条部门数据")

    async with async_session() as db:
        # 清空旧数据（先删子节点再删父节点，通过反向排序实现）
        existing = (await db.execute(select(Department))).scalars().all()
        if existing:
            print(f"清空旧数据 {len(existing)} 条")
            for dept in reversed(existing):
                await db.delete(dept)
            await db.commit()

        for item in flat:
            db.add(Department(**item))
        await db.commit()
        print(f"成功插入 {len(flat)} 条部门数据（UUID 主键）")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
