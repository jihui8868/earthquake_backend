from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    name: str
    parentId: str | None = None
    sort: int = 0
    leader: str = ""
    phone: str = ""
    status: int = 1
    remark: str = ""


class DepartmentUpdate(DepartmentCreate):
    pass


class DepartmentOut(BaseModel):
    id: str
    name: str
    parentId: str | None = None
    sort: int = 0
    leader: str = ""
    phone: str = ""
    status: int = 1
    remark: str = ""
    children: list["DepartmentOut"] = []

    model_config = {"from_attributes": True}
