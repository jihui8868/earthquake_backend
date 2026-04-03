from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file_system import FileItem


async def get_all(db: AsyncSession) -> list[FileItem]:
    result = await db.execute(select(FileItem))
    return list(result.scalars().all())


async def get_by_parent(db: AsyncSession, parent_id: str | None = None) -> list[FileItem]:
    query = select(FileItem).where(FileItem.parent_id == parent_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, file_id: str) -> FileItem | None:
    return await db.get(FileItem, file_id)


async def create_folder(db: AsyncSession, *, name: str,
                         parent_id: str | None = None) -> FileItem:
    folder = FileItem(name=name, parent_id=parent_id, is_folder=True)
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


async def create_file(db: AsyncSession, *, name: str, parent_id: str | None = None,
                      size: int = 0, path: str = "") -> FileItem:
    file_item = FileItem(
        name=name, parent_id=parent_id,
        is_folder=False, size=size, path=path,
    )
    db.add(file_item)
    await db.commit()
    await db.refresh(file_item)
    return file_item


async def rename(db: AsyncSession, item: FileItem, name: str) -> FileItem:
    item.name = name
    await db.commit()
    await db.refresh(item)
    return item


async def move(db: AsyncSession, item: FileItem,
               target_parent_id: str | None) -> FileItem:
    item.parent_id = target_parent_id
    await db.commit()
    await db.refresh(item)
    return item


async def delete(db: AsyncSession, item: FileItem) -> None:
    await db.delete(item)
    await db.commit()
