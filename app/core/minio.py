import logging

from minio import Minio

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


def create_minio_client() -> Minio:
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


def ensure_bucket(client: Minio, bucket: str = settings.MINIO_BUCKET) -> None:
    """确保 bucket 存在，不存在则创建。"""
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        logger.info(f"MinIO bucket '{bucket}' 已创建")
    else:
        logger.info(f"MinIO bucket '{bucket}' 已存在")


minio_client = create_minio_client()
