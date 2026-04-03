from pydantic import BaseModel


class KGFileOut(BaseModel):
    id: str
    name: str
    size: int = 0
    status: str = "pending"
    createTime: str = ""

    model_config = {"from_attributes": True}


class KGNodeOut(BaseModel):
    id: str
    name: str
    type: str = ""
    weight: float = 1.0
    properties: dict = {}

    model_config = {"from_attributes": True}


class KGRelationOut(BaseModel):
    id: str
    sourceId: str
    targetId: str
    type: str = ""

    model_config = {"from_attributes": True}


class GraphData(BaseModel):
    nodes: list[KGNodeOut] = []
    relations: list[KGRelationOut] = []


class GraphStats(BaseModel):
    nodeCount: int = 0
    relationCount: int = 0
    fileCount: int = 0
