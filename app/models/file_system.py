import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FileItem(Base):
    __tablename__ = "file_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("file_items.id"), nullable=True)
    is_folder: Mapped[bool] = mapped_column(Boolean, default=False)
    size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    path: Mapped[str] = mapped_column(String(1000), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    children = relationship("FileItem", back_populates="parent_item", lazy="selectin")
    parent_item = relationship("FileItem", back_populates="children", remote_side=[id], lazy="selectin")
