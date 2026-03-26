from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.sql import func

from app.core.database import Base

collection_items = Table(
    "collection_items",
    Base.metadata,
    Column("collection_id", String, ForeignKey("collections.id", ondelete="CASCADE")),
    Column("item_id", String),
    Column("item_type", String),  # source | note
)


class Collection(Base):
    __tablename__ = "collections"

    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())
