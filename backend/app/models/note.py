from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func

from app.core.database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True)
    title = Column(String)
    content = Column(String)  # plain markdown
    gdrive_file_id = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    synced_at = Column(DateTime)
