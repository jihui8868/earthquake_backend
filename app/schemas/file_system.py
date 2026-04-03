from pydantic import BaseModel


class FolderCreate(BaseModel):
    name: str
    parentId: str | None = None


class FileRename(BaseModel):
    name: str


class FileMove(BaseModel):
    targetParentId: str | None = None


class FileOut(BaseModel):
    id: str
    name: str
    parentId: str | None = None
    isFolder: bool = False
    size: int | None = None
    createTime: str = ""
    children: list["FileOut"] = []

    model_config = {"from_attributes": True}
