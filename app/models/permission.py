import uuid
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(100), default="")
    parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("permissions.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(20), default="menu")
    path: Mapped[str] = mapped_column(String(200), default="")
    icon: Mapped[str] = mapped_column(String(100), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)
    remark: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    children = relationship("Permission", back_populates="parent", lazy="selectin")
    parent = relationship("Permission", back_populates="children", remote_side=[id], lazy="selectin")
