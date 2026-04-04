import logging

from pymilvus import connections, utility

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

MILVUS_ALIAS = "default"


def connect_milvus() -> None:
    """建立 Milvus 连接。"""
    connections.connect(
        alias=MILVUS_ALIAS,
        host=settings.MILVUS_HOST,
        port=settings.MILVUS_PORT,
        db_name=settings.MILVUS_DATABASE,
    )
    logger.info(f"Milvus 连接成功: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")


def disconnect_milvus() -> None:
    """断开 Milvus 连接。"""
    connections.disconnect(alias=MILVUS_ALIAS)
    logger.info("Milvus 连接已关闭")


def check_connection() -> bool:
    """检查 Milvus 连接是否正常。"""
    try:
        utility.list_collections(using=MILVUS_ALIAS)
        return True
    except Exception:
        return False
