from sqlalchemy import Column, String, Table, ForeignKey
from app.core.database import Base

source_tags = Table(
    "source_tags",
    Base.metadata,
    Column("source_id", String, ForeignKey("sources.id", ondelete="CASCADE")),
    Column("tag_id", String, ForeignKey("tags.id", ondelete="CASCADE")),
)

note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", String, ForeignKey("notes.id", ondelete="CASCADE")),
    Column("tag_id", String, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    color = Column(String, default="#6b7280")
