from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func

from app.core.database import Base


class SyncLog(Base):
    __tablename__ = "sync_log"

    id = Column(String, primary_key=True)
    entity_id = Column(String)
    entity_type = Column(String)  # source | note | annotation
    action = Column(String)       # create | update | delete
    gdrive_file_id = Column(String)
    status = Column(String)       # pending | done | conflict | failed
    error = Column(String)
    synced_at = Column(DateTime, server_default=func.now())
