"""Milvus 向量数据库 CRUD 操作。"""

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    utility,
)

from app.core.milvus import MILVUS_ALIAS


# ── Collection 管理 ──

def create_collection(
    name: str,
    dim: int = 768,
    description: str = "",
    id_field: str = "id",
    vector_field: str = "embedding",
    extra_fields: list[FieldSchema] | None = None,
) -> Collection:
    """创建集合。默认包含 id(VARCHAR) + text(VARCHAR) + embedding(FLOAT_VECTOR) 三个字段。"""
    fields = [
        FieldSchema(name=id_field, dtype=DataType.VARCHAR, is_primary=True, max_length=36),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name=vector_field, dtype=DataType.FLOAT_VECTOR, dim=dim),
    ]
    if extra_fields:
        fields.extend(extra_fields)

    schema = CollectionSchema(fields=fields, description=description)
    collection = Collection(name=name, schema=schema, using=MILVUS_ALIAS)
    return collection


def get_collection(name: str) -> Collection:
    """获取已有集合。"""
    return Collection(name=name, using=MILVUS_ALIAS)


def list_collections() -> list[str]:
    """列出所有集合。"""
    return utility.list_collections(using=MILVUS_ALIAS)


def drop_collection(name: str) -> None:
    """删除集合。"""
    utility.drop_collection(name, using=MILVUS_ALIAS)


def collection_exists(name: str) -> bool:
    """判断集合是否存在。"""
    return utility.has_collection(name, using=MILVUS_ALIAS)


# ── Index 管理 ──

def create_index(
    collection_name: str,
    field_name: str = "embedding",
    index_type: str = "IVF_FLAT",
    metric_type: str = "COSINE",
    nlist: int = 128,
) -> None:
    """为向量字段创建索引。"""
    col = get_collection(collection_name)
    index_params = {
        "index_type": index_type,
        "metric_type": metric_type,
        "params": {"nlist": nlist},
    }
    col.create_index(field_name=field_name, index_params=index_params)
    col.load()


# ── 数据 CRUD ──

def insert(
    collection_name: str,
    ids: list[str],
    texts: list[str],
    embeddings: list[list[float]],
) -> int:
    """插入数据，返回插入条数。"""
    col = get_collection(collection_name)
    col.insert([ids, texts, embeddings])
    col.flush()
    return len(ids)


def search(
    collection_name: str,
    query_vectors: list[list[float]],
    top_k: int = 10,
    vector_field: str = "embedding",
    metric_type: str = "COSINE",
    output_fields: list[str] | None = None,
    search_params: dict | None = None,
) -> list[list[dict]]:
    """向量相似度搜索，返回结果列表。"""
    col = get_collection(collection_name)
    col.load()

    if output_fields is None:
        output_fields = ["id", "text"]
    if search_params is None:
        search_params = {"metric_type": metric_type, "params": {"nprobe": 16}}

    results = col.search(
        data=query_vectors,
        anns_field=vector_field,
        param=search_params,
        limit=top_k,
        output_fields=output_fields,
    )

    return [
        [
            {"id": hit.id, "distance": hit.distance, **hit.entity.to_dict().get("entity", {})}
            for hit in hits
        ]
        for hits in results
    ]


def query(
    collection_name: str,
    filter_expr: str,
    output_fields: list[str] | None = None,
    limit: int = 100,
) -> list[dict]:
    """按条件查询数据。"""
    col = get_collection(collection_name)
    col.load()

    if output_fields is None:
        output_fields = ["id", "text"]

    results = col.query(
        expr=filter_expr,
        output_fields=output_fields,
        limit=limit,
    )
    return results


def delete(
    collection_name: str,
    filter_expr: str,
) -> None:
    """按条件删除数据。如 delete("my_col", 'id in ["a1","a2"]')"""
    col = get_collection(collection_name)
    col.delete(filter_expr)
    col.flush()


def count(collection_name: str) -> int:
    """获取集合中的数据总数。"""
    col = get_collection(collection_name)
    col.flush()
    return col.num_entities
