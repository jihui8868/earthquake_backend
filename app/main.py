import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, Base
from app.models import *  # noqa: F401, F403 — ensure all models are registered
from app.router import chat, department, user, role, permission, knowledge_base, knowledge_graph, file_system

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 连接数据库并验证
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"数据库连接成功: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")
            logger.info(f"PostgreSQL 版本: {version}")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库表创建/检查完成")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise
    # 连接 MinIO 并确保 bucket 存在
    try:
        from app.core.minio import minio_client, ensure_bucket
        ensure_bucket(minio_client)
        logger.info(f"MinIO 连接成功: {settings.MINIO_ENDPOINT}, bucket: {settings.MINIO_BUCKET}")
    except Exception as e:
        logger.error(f"MinIO 连接失败: {e}")
        raise
    # 连接 Milvus
    try:
        from app.core.milvus import connect_milvus, disconnect_milvus, check_connection
        connect_milvus()
        if check_connection():
            logger.info(f"Milvus 连接验证通过: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
        else:
            raise RuntimeError("Milvus 连接验证失败")
    except Exception as e:
        logger.error(f"Milvus 连接失败: {e}")
        raise
    # 连接 Neo4j
    try:
        from app.core.neo4j import connect_neo4j, disconnect_neo4j
        connect_neo4j()
    except Exception as e:
        logger.error(f"Neo4j 连接失败: {e}")
        raise
    yield
    disconnect_neo4j()
    disconnect_milvus()
    await engine.dispose()
    logger.info("所有连接已关闭")


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

# Register routers under /api prefix
for r in [chat, department, user, role, permission, knowledge_base, knowledge_graph, file_system]:
    app.include_router(r.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
