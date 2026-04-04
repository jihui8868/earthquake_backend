"""Neo4j 图数据库 CRUD 操作。"""

from typing import Any

from app.core.config import settings
from app.core.neo4j import get_driver


def _run(query: str, parameters: dict | None = None, **kwargs) -> list[dict[str, Any]]:
    """执行 Cypher 查询并返回结果列表。"""
    driver = get_driver()
    with driver.session(database=settings.NEO4J_DATABASE) as session:
        result = session.run(query, parameters=parameters, **kwargs)
        return [record.data() for record in result]


# ── 节点 CRUD ──

def create_node(label: str, properties: dict) -> dict:
    """创建节点，返回节点属性。"""
    records = _run(
        f"CREATE (n:{label} $props) RETURN n",
        parameters={"props": properties},
    )
    return records[0]["n"] if records else {}


def get_node_by_id(element_id: str) -> dict | None:
    """通过 elementId 获取节点。"""
    records = _run(
        "MATCH (n) WHERE elementId(n) = $eid RETURN n",
        parameters={"eid": element_id},
    )
    return records[0]["n"] if records else None


def find_nodes(label: str, filters: dict | None = None, limit: int = 100) -> list[dict]:
    """按标签和属性条件查找节点。"""
    where_clause = ""
    params: dict[str, Any] = {"limit": limit}
    if filters:
        conditions = [f"n.{k} = ${k}" for k in filters]
        where_clause = "WHERE " + " AND ".join(conditions)
        params.update(filters)

    records = _run(
        f"MATCH (n:{label}) {where_clause} RETURN n LIMIT $limit",
        parameters=params,
    )
    return [r["n"] for r in records]


def search_nodes(label: str, field: str, keyword: str, limit: int = 100) -> list[dict]:
    """模糊搜索节点。"""
    records = _run(
        f"MATCH (n:{label}) WHERE n.{field} CONTAINS $keyword RETURN n LIMIT $limit",
        parameters={"keyword": keyword, "limit": limit},
    )
    return [r["n"] for r in records]


def update_node(element_id: str, properties: dict) -> dict | None:
    """更新节点属性。"""
    records = _run(
        "MATCH (n) WHERE elementId(n) = $eid SET n += $props RETURN n",
        parameters={"eid": element_id, "props": properties},
    )
    return records[0]["n"] if records else None


def delete_node(element_id: str) -> bool:
    """删除节点及其关系。"""
    records = _run(
        "MATCH (n) WHERE elementId(n) = $eid DETACH DELETE n RETURN count(n) AS cnt",
        parameters={"eid": element_id},
    )
    return records[0]["cnt"] > 0 if records else False


# ── 关系 CRUD ──

def create_relation(
    from_id: str, to_id: str, rel_type: str, properties: dict | None = None,
) -> dict:
    """创建关系，返回关系属性。"""
    props = properties or {}
    records = _run(
        f"MATCH (a), (b) WHERE elementId(a) = $fid AND elementId(b) = $tid "
        f"CREATE (a)-[r:{rel_type} $props]->(b) RETURN type(r) AS type, properties(r) AS props",
        parameters={"fid": from_id, "tid": to_id, "props": props},
    )
    return records[0] if records else {}


def get_relations(element_id: str, direction: str = "both") -> list[dict]:
    """获取节点的所有关系。direction: out / in / both。"""
    if direction == "out":
        pattern = "(a)-[r]->(b)"
    elif direction == "in":
        pattern = "(a)<-[r]-(b)"
    else:
        pattern = "(a)-[r]-(b)"

    records = _run(
        f"MATCH {pattern} WHERE elementId(a) = $eid "
        "RETURN type(r) AS type, properties(r) AS props, "
        "elementId(r) AS relId, elementId(b) AS targetId, labels(b) AS targetLabels, properties(b) AS target",
        parameters={"eid": element_id},
    )
    return records


def delete_relation(rel_element_id: str) -> bool:
    """通过 elementId 删除关系。"""
    records = _run(
        "MATCH ()-[r]-() WHERE elementId(r) = $rid DELETE r RETURN count(r) AS cnt",
        parameters={"rid": rel_element_id},
    )
    return records[0]["cnt"] > 0 if records else False


# ── 图查询 ──

def get_graph(label: str | None = None, limit: int = 200) -> dict:
    """获取图数据（节点 + 关系），用于可视化。"""
    label_filter = f":{label}" if label else ""
    records = _run(
        f"MATCH (n{label_filter}) "
        "OPTIONAL MATCH (n)-[r]-(m) "
        "RETURN DISTINCT n, collect(DISTINCT r) AS rels, collect(DISTINCT m) AS neighbors "
        "LIMIT $limit",
        parameters={"limit": limit},
    )

    nodes_map: dict[str, dict] = {}
    relations_list: list[dict] = []

    for record in records:
        n = record["n"]
        node_key = str(n.get("name", id(n)))
        if node_key not in nodes_map:
            nodes_map[node_key] = n

        for neighbor in record.get("neighbors", []):
            if neighbor:
                nk = str(neighbor.get("name", id(neighbor)))
                if nk not in nodes_map:
                    nodes_map[nk] = neighbor

    # 单独查关系
    rel_records = _run(
        f"MATCH (a{label_filter})-[r]->(b) "
        "RETURN elementId(a) AS sourceId, elementId(b) AS targetId, "
        "type(r) AS type, properties(r) AS props "
        "LIMIT $limit",
        parameters={"limit": limit},
    )
    relations_list = rel_records

    return {"nodes": list(nodes_map.values()), "relations": relations_list}


def run_cypher(query: str, parameters: dict | None = None) -> list[dict]:
    """执行任意 Cypher 查询。"""
    return _run(query, parameters=parameters)


def count_nodes(label: str | None = None) -> int:
    """统计节点数量。"""
    label_filter = f":{label}" if label else ""
    records = _run(f"MATCH (n{label_filter}) RETURN count(n) AS cnt")
    return records[0]["cnt"] if records else 0


def count_relations(rel_type: str | None = None) -> int:
    """统计关系数量。"""
    type_filter = f":{rel_type}" if rel_type else ""
    records = _run(f"MATCH ()-[r{type_filter}]-() RETURN count(r) AS cnt")
    return records[0]["cnt"] if records else 0
