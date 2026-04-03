from pydantic import BaseModel


class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str = ""
    categoryId: str | None = None
    type: str = "public"
    enabled: bool = True


class KnowledgeBaseUpdate(KnowledgeBaseCreate):
    pass


class KnowledgeBaseOut(BaseModel):
    id: str
    name: str
    description: str = ""
    categoryId: str | None = None
    type: str = "public"
    enabled: bool = True

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name: str
    parentId: str | None = None


class CategoryOut(BaseModel):
    id: str
    name: str
    parentId: str | None = None
    count: int = 0
    children: list["CategoryOut"] = []

    model_config = {"from_attributes": True}
