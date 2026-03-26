from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.sql import func

from app.core.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(String, primary_key=True)
    title = Column(String)
    type = Column(String)  # pdf | url | doi | arxiv | youtube | audio | image | text
    url = Column(String)
    doi = Column(String)
    arxiv_id = Column(String)
    pubmed_id = Column(String)
    gdrive_file_id = Column(String)
    gdrive_folder_id = Column(String)
    local_cache_path = Column(String)
    status = Column(String, default="pending")  # pending | processing | ready | failed
    error = Column(String)
    source_metadata = Column("metadata", JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    synced_at = Column(DateTime)
