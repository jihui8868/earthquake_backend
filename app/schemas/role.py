from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str
    code: str
    sort: int = 0
    status: int = 1
    remark: str = ""


class RoleUpdate(RoleCreate):
    pass


class RoleOut(BaseModel):
    id: str
    name: str
    code: str
    sort: int = 0
    status: int = 1
    remark: str = ""

    model_config = {"from_attributes": True}


class RolePermissionUpdate(BaseModel):
    permissionIds: list[str] = []
