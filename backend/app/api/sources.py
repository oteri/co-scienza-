import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.source import Source
from app.workers.ingest_tasks import ingest_source

router = APIRouter()

SourceType = Literal["url", "pdf", "doi", "arxiv", "pubmed", "youtube", "audio", "image", "text"]


class SourceCreate(BaseModel):
    type: SourceType
    url: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    pubmed_id: str | None = None
    text: str | None = None
    title: str | None = None


class SourceRead(BaseModel):
    id: str
    title: str | None
    type: str
    url: str | None
    status: str
    source_metadata: dict | None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[SourceRead])
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source).order_by(Source.created_at.desc()))
    return result.scalars().all()


@router.post("/", response_model=SourceRead, status_code=201)
async def create_source(body: SourceCreate, db: AsyncSession = Depends(get_db)):
    source = Source(
        id=str(uuid.uuid4()),
        type=body.type,
        url=body.url,
        doi=body.doi,
        arxiv_id=body.arxiv_id,
        pubmed_id=body.pubmed_id,
        title=body.title,
        status="pending",
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)
    ingest_source.delay(source.id, body.model_dump())
    return source


@router.post("/upload", response_model=SourceRead, status_code=201)
async def upload_file(file: UploadFile, db: AsyncSession = Depends(get_db)):
    content = await file.read()
    source = Source(
        id=str(uuid.uuid4()),
        type="pdf",
        title=file.filename,
        status="pending",
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)
    ingest_source.delay(source.id, {"type": "pdf", "filename": file.filename, "content": content.hex()})
    return source


@router.get("/{source_id}", response_model=SourceRead)
async def get_source(source_id: str, db: AsyncSession = Depends(get_db)):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.delete("/{source_id}", status_code=204)
async def delete_source(source_id: str, db: AsyncSession = Depends(get_db)):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    await db.delete(source)
    await db.commit()
