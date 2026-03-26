from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from app.core.database import Base


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(String, primary_key=True)
    source_id = Column(String, ForeignKey("sources.id", ondelete="CASCADE"))
    type = Column(String)  # highlight | note | question | key-claim
    content = Column(String)  # plain markdown
    position = Column(JSON)   # {page, char_start, char_end}
    color = Column(String)
    created_at = Column(DateTime, server_default=func.now())
