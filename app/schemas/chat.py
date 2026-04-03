from pydantic import BaseModel


class ChatSource(BaseModel):
    key: str = ""
    type: str = ""
    name: str = ""


class ChatSend(BaseModel):
    sessionId: str
    content: str
    sources: list[ChatSource] = []


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    sources: list[ChatSource] = []
    time: str = ""

    model_config = {"from_attributes": True}


class ChatSessionOut(BaseModel):
    id: str
    title: str = "新对话"
    createTime: str = ""

    model_config = {"from_attributes": True}
