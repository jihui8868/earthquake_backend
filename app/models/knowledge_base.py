import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class KnowledgeBaseCategory(Base):
    __tablename__ = "knowledge_base_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("knowledge_base_categories.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    children = relationship("KnowledgeBaseCategory", back_populates="parent", lazy="selectin")
    parent = relationship("KnowledgeBaseCategory", back_populates="children", remote_side=[id], lazy="selectin")
    knowledge_bases = relationship("KnowledgeBase", back_populates="category", lazy="selectin")


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), default="")
    category_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("knowledge_base_categories.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(20), default="public")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    category = relationship("KnowledgeBaseCategory", back_populates="knowledge_bases", lazy="selectin")
