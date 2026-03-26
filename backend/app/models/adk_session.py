from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.sql import func

from app.core.database import Base


class AdkSession(Base):
    __tablename__ = "adk_sessions"

    session_id = Column(String, primary_key=True)
    state = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
