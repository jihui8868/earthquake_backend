from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    nickname: str = ""
    email: str = ""
    phone: str = ""
    deptId: str | None = None
    roleId: str | None = None
    status: int = 1
    remark: str = ""


class UserUpdate(UserCreate):
    pass


class UserOut(BaseModel):
    id: str
    username: str
    nickname: str = ""
    email: str = ""
    phone: str = ""
    deptId: str | None = None
    deptName: str = ""
    roleId: str | None = None
    roleName: str = ""
    status: int = 1
    remark: str = ""

    model_config = {"from_attributes": True}
