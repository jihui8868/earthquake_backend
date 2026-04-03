from pydantic import BaseModel


class PermissionCreate(BaseModel):
    name: str
    code: str = ""
    parentId: str | None = None
    type: str = "menu"
    path: str = ""
    icon: str = ""
    sort: int = 0
    status: int = 1
    remark: str = ""


class PermissionUpdate(PermissionCreate):
    pass


class PermissionOut(BaseModel):
    id: str
    name: str
    code: str = ""
    parentId: str | None = None
    type: str = "menu"
    path: str = ""
    icon: str = ""
    sort: int = 0
    status: int = 1
    remark: str = ""
    children: list["PermissionOut"] = []

    model_config = {"from_attributes": True}
