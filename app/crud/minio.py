"""MinIO 文件存储 CRUD 操作。"""

import io
from datetime import timedelta

from minio import Minio

from app.core.config import settings
from app.core.minio import minio_client, ensure_bucket


def upload_file(
    object_name: str,
    data: bytes,
    content_type: str = "application/octet-stream",
    bucket: str = settings.MINIO_BUCKET,
    client: Minio = minio_client,
) -> str:
    """上传文件，返回 object_name。"""
    ensure_bucket(client, bucket)
    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return object_name


def download_file(
    object_name: str,
    bucket: str = settings.MINIO_BUCKET,
    client: Minio = minio_client,
) -> bytes:
    """下载文件，返回文件内容字节。"""
    response = client.get_object(bucket_name=bucket, object_name=object_name)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def get_presigned_url(
    object_name: str,
    expires: timedelta = timedelta(hours=1),
    bucket: str = settings.MINIO_BUCKET,
    client: Minio = minio_client,
) -> str:
    """获取文件的预签名下载 URL。"""
    return client.presigned_get_object(
        bucket_name=bucket,
        object_name=object_name,
        expires=expires,
    )


def delete_file(
    object_name: str,
    bucket: str = settings.MINIO_BUCKET,
    client: Minio = minio_client,
) -> None:
    """删除文件。"""
    client.remove_object(bucket_name=bucket, object_name=object_name)


def list_files(
    prefix: str = "",
    recursive: bool = True,
    bucket: str = settings.MINIO_BUCKET,
    client: Minio = minio_client,
) -> list[dict]:
    """列出文件，返回对象信息列表。"""
    objects = client.list_objects(
        bucket_name=bucket,
        prefix=prefix,
        recursive=recursive,
    )
    return [
        {
            "name": obj.object_name,
            "size": obj.size,
            "lastModified": obj.last_modified.isoformat() if obj.last_modified else "",
            "contentType": obj.content_type or "",
        }
        for obj in objects
    ]


def file_exists(
    object_name: str,
    bucket: str = settings.MINIO_BUCKET,
    client: Minio = minio_client,
) -> bool:
    """判断文件是否存在。"""
    try:
        client.stat_object(bucket_name=bucket, object_name=object_name)
        return True
    except Exception:
        return False
