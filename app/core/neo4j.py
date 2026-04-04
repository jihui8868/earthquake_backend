import logging

from neo4j import GraphDatabase, Driver

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

_driver: Driver | None = None


def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
    return _driver


def connect_neo4j() -> None:
    """建立连接并验证。"""
    driver = get_driver()
    driver.verify_connectivity()
    logger.info(f"Neo4j 连接成功: {settings.NEO4J_URI}")


def disconnect_neo4j() -> None:
    """关闭连接。"""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
        logger.info("Neo4j 连接已关闭")
