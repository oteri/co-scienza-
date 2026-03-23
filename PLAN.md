# co-scienza — Product Plan

> A personal, offline-first knowledge management system combining the best of Zotero,
> NotebookLM, Obsidian, and Notion — built mobile-first with Expo + React Native.

---

## Vision

co-scienza is a **personal, offline-first knowledge base** for capturing, reading, annotating,
and querying any type of source — papers, web pages, videos, audio, notes — with AI as a
built-in layer for extraction and chat.

Your data lives **on your terms**: stored as plain markdown + PDFs synced to Google Drive,
with a local SQLite index for fast search and AI grounding.

---

## Core Principles

1. **Data ownership** — all content stored as plain markdown + PDFs on Google Drive. Human-readable without the app.
2. **Offline-first** — fully functional without internet; GDrive sync happens in the background.
3. **AI from day one** — chat with your sources (NotebookLM-style) powered by Google ADK + Gemini.
4. **Mobile-first** — designed for iOS/Android first, accessible on web via Expo Web.
5. **Personal tool** — no multi-tenancy, no sharing complexity. Just you and your knowledge.
6. **Plain markdown everywhere** — notes, annotations, extractions: all stored as `.md` files. No proprietary formats.

---

## Tech Stack

### Frontend — Expo (React Native)

| Concern | Choice | Notes |
|---|---|---|
| Framework | **Expo SDK** (React Native) | iOS, Android, Web (Expo Web) |
| Navigation | **Expo Router** | File-based routing, works on web too |
| Editor | **Plain `TextInput`** + `react-native-markdown-display` | Edit/preview toggle — simple, no deps |
| PDF viewer | **react-native-pdf** | Mobile; web fallback via iframe |
| Styling | **NativeWind** (Tailwind for RN) | Consistent design system cross-platform |
| State | **Zustand** | Lightweight, works offline-first |
| Local DB | **expo-sqlite** | Local mirror of sources, notes, annotations |
| File cache | **expo-file-system** | PDFs and markdown cached on device |
| Networking | **TanStack Query** | Cache, retry, background refetch |
| Share intent | **expo-share-intent** | Intercept shared URLs/files from other apps |
| PWA / Web | **Expo Web** | Same codebase, browser-accessible |

### Backend — Python FastAPI

| Concern | Choice | Notes |
|---|---|---|
| Framework | **FastAPI** | Async, typed, fast |
| Database | **SQLite** via **SQLAlchemy** + **Alembic** | Single-file DB, self-hosted friendly |
| Vector store | **sqlite-vec** | Embedded vectors in SQLite — zero extra services |
| Background jobs | **Celery** + **Redis** | Ingestion, embedding, sync jobs |
| GDrive sync | **google-api-python-client** | Read/write files, manage folder structure |
| AI framework | **Google ADK** (`google-adk`) | Agent orchestration, tool use, grounding |
| Gemini SDK | **Google GenAI SDK** (`google-genai`) | Underlying model access (ADK depends on this) |
| Grounding / RAG | **ADK custom retrieval tool** → sqlite-vec | Self-hosted RAG; Vertex AI RAG Engine as upgrade path |
| Gemini model | **`gemini-2.5-flash`** (default) | Fast, large context, free tier available |
| PDF extraction | **pypdf** + **pymupdf** | Text and page-level extraction |
| Web scraping | **httpx** + **trafilatura** | URL → clean article markdown |
| YouTube | **youtube-transcript-api** | Fetch transcripts by URL/ID |
| Audio | **faster-whisper** (local) or Gemini audio input | Transcription — configurable |
| OCR / images | Gemini multimodal (`gemini-2.5-flash`) | Image → description/text |
| Academic APIs | CrossRef, arXiv, PubMed (via httpx) | DOI / arXiv ID / PubMed ID resolution |

### Infrastructure

| Concern | Choice |
|---|---|
| Containerization | **Docker Compose** |
| Services | `backend`, `worker`, `redis`, optional `web` (nginx) |
| Reverse proxy | **Caddy** (optional, for HTTPS on self-hosted) |

---

## Monorepo Structure

```
co-scienza/
├── apps/
│   └── mobile/                    ← Expo app (iOS, Android, Web)
│       ├── app/                   ← Expo Router screens
│       │   ├── (tabs)/
│       │   │   ├── library.tsx    ← source library
│       │   │   ├── notes.tsx      ← notes list
│       │   │   └── chat.tsx       ← AI chat
│       │   ├── source/[id].tsx    ← source detail + reader
│       │   ├── note/[id].tsx      ← markdown editor/preview
│       │   └── settings.tsx
│       ├── components/
│       ├── hooks/
│       ├── store/                 ← Zustand stores
│       └── lib/
│           ├── api.ts             ← FastAPI client
│           └── sync.ts            ← offline sync logic
├── backend/
│   ├── app/
│   │   ├── api/                   ← FastAPI routers
│   │   │   ├── sources.py
│   │   │   ├── notes.py
│   │   │   ├── chat.py            ← ADK chat endpoint (SSE streaming)
│   │   │   └── sync.py
│   │   ├── models/                ← SQLAlchemy models
│   │   ├── services/
│   │   │   ├── ingest/            ← one module per source type
│   │   │   │   ├── pdf.py
│   │   │   │   ├── url.py
│   │   │   │   ├── doi.py
│   │   │   │   ├── arxiv.py
│   │   │   │   ├── youtube.py
│   │   │   │   ├── audio.py
│   │   │   │   └── image.py
│   │   │   ├── ai/
│   │   │   │   ├── agent.py       ← ADK root agent definition
│   │   │   │   ├── tools.py       ← retrieve_from_library, search_sources, etc.
│   │   │   │   └── embeddings.py  ← chunk + embed pipeline
│   │   │   └── gdrive/
│   │   │       ├── client.py      ← GDrive API wrapper
│   │   │       └── sync.py        ← bidirectional sync engine
│   │   ├── workers/               ← Celery task definitions
│   │   └── main.py
│   ├── alembic/                   ← DB migrations
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── PLAN.md
```

---

## GDrive File Structure

```
GDrive: /co-scienza/
├── sources/
│   └── {year}/
│       └── {slug}/
│           ├── source.pdf          ← original file (if applicable)
│           ├── metadata.json       ← structured metadata (authors, year, etc.)
│           ├── content.md          ← extracted/scraped text as markdown
│           └── annotations.md      ← highlights + notes (plain markdown)
├── notes/
│   └── {slug}.md                   ← standalone notes (plain markdown)
├── collections/
│   └── {name}.json
└── config.json                     ← AI provider config, sync prefs
```

---

## Data Model (SQLite)

```sql
CREATE TABLE sources (
  id TEXT PRIMARY KEY,
  title TEXT,
  type TEXT,          -- pdf | url | doi | arxiv | youtube | audio | image | text
  url TEXT,
  doi TEXT, arxiv_id TEXT,
  gdrive_file_id TEXT,
  local_cache_path TEXT,
  status TEXT,        -- pending | processing | ready | failed
  metadata JSON,      -- authors, year, journal, abstract, duration, etc.
  created_at DATETIME, updated_at DATETIME, synced_at DATETIME
);

CREATE TABLE annotations (
  id TEXT PRIMARY KEY,
  source_id TEXT REFERENCES sources(id),
  type TEXT,          -- highlight | note | question | key-claim
  content TEXT,       -- plain markdown
  position JSON,      -- {page, char_start, char_end}
  color TEXT,
  created_at DATETIME
);

CREATE TABLE notes (
  id TEXT PRIMARY KEY,
  title TEXT,
  content TEXT,       -- plain markdown
  gdrive_file_id TEXT,
  created_at DATETIME, updated_at DATETIME
);

CREATE TABLE tags (id TEXT PRIMARY KEY, name TEXT, color TEXT);
CREATE TABLE source_tags (source_id TEXT, tag_id TEXT);
CREATE TABLE note_tags (note_id TEXT, tag_id TEXT);

CREATE TABLE links (
  from_id TEXT, from_type TEXT,   -- source | note
  to_id TEXT,   to_type TEXT
);

CREATE TABLE collections (
  id TEXT PRIMARY KEY, name TEXT, description TEXT, created_at DATETIME
);
CREATE TABLE collection_items (
  collection_id TEXT, item_id TEXT, item_type TEXT  -- source | note
);

-- Chunks + embeddings for RAG
CREATE TABLE chunks (
  id TEXT PRIMARY KEY,
  entity_id TEXT, entity_type TEXT,  -- source | note | annotation
  chunk_text TEXT,
  chunk_index INTEGER,
  model_id TEXT,
  vector BLOB    -- via sqlite-vec
);

CREATE TABLE sync_log (
  id TEXT PRIMARY KEY,
  entity_id TEXT, entity_type TEXT,
  action TEXT,   -- create | update | delete
  gdrive_file_id TEXT,
  status TEXT,   -- pending | done | conflict | failed
  synced_at DATETIME
);

-- ADK session persistence
CREATE TABLE adk_sessions (
  session_id TEXT PRIMARY KEY,
  state JSON,
  created_at DATETIME, updated_at DATETIME
);
```

---

## AI Architecture — Google ADK

### Agent definition (`agent.py`)

```python
from google.adk.agents import Agent
from app.services.ai.tools import (
    retrieve_from_library,
    search_sources_by_metadata,
    get_source_content,
)

root_agent = Agent(
    name="coscienza_assistant",
    model="gemini-2.5-flash",
    description="Personal knowledge assistant. Answers questions grounded in the user's library.",
    instruction="""You are a personal research assistant with access to the user's knowledge library.
Always ground your answers in the retrieved content. Cite sources with title and page/section.
If you don't find relevant content, say so clearly.""",
    tools=[
        retrieve_from_library,   # semantic vector search → returns chunks
        search_sources_by_metadata,  # filter by author, year, type, tag
        get_source_content,      # fetch full content of a specific source
    ],
)
```

### Streaming chat endpoint

```python
# POST /api/chat  →  SSE stream
# - Creates or resumes an ADK session
# - Streams Gemini response tokens as Server-Sent Events
# - Citations attached to response events
```

### RAG tool (custom, self-hosted)

```python
@tool
async def retrieve_from_library(query: str, top_k: int = 5) -> list[dict]:
    """Retrieve relevant chunks from the user's library using semantic search."""
    embedding = await embed(query)
    chunks = sqlite_vec_search(embedding, top_k)
    return [{"text": c.chunk_text, "source": c.entity_id, "title": c.title} for c in chunks]
```

**Upgrade path**: swap `sqlite_vec_search` for `VertexAiRagRetrieval` if moving to Vertex AI RAG Engine (no agent code changes needed).

---

## Feature Phases

### Phase 1 — Foundation + Ingestion + Chat with Sources (MVP)

**Goal**: Import any content, store in GDrive, and immediately chat with it.

#### Backend setup
- [ ] FastAPI project, SQLAlchemy models, Alembic migrations
- [ ] SQLite + sqlite-vec initialization
- [ ] Google OAuth → GDrive access token storage
- [ ] GDrive folder structure initialization on first run
- [ ] Celery + Redis worker setup
- [ ] Docker Compose: `backend`, `worker`, `redis`

#### Importers (Celery tasks)
- [ ] **PDF upload** — pypdf text extraction → chunk → embed → GDrive
- [ ] **URL** — trafilatura → markdown → chunk → embed → GDrive
- [ ] **DOI** — CrossRef API → metadata + Unpaywall PDF → GDrive
- [ ] **arXiv ID / URL** — arXiv API → metadata + PDF → GDrive
- [ ] **PubMed ID** — NCBI API → metadata + PDF fallback
- [ ] **YouTube URL** — youtube-transcript-api → markdown → chunk → embed → GDrive
- [ ] **Audio file** — faster-whisper → transcript markdown → chunk → embed → GDrive
- [ ] **Image** — Gemini multimodal → description markdown → embed → GDrive
- [ ] **Plain text / markdown paste** — direct input → embed → GDrive

#### Share intent (mobile)
- [ ] **expo-share-intent** configured for iOS Share Extension + Android intent filters
- [ ] Shared URL / file opens app → bottom sheet with pre-filled import form
- [ ] Background import if app is closed (Expo Background Task)

#### Source library (mobile UI)
- [ ] Source list screen: search, filter by type / tag / status
- [ ] Import bottom sheet: pick type or auto-detect from URL/file
- [ ] Import status polling (pending → processing → ready)
- [ ] Source detail screen: metadata, tags, quick actions

#### Chat with sources (ADK)
- [ ] ADK root agent + tools wired up (`retrieve_from_library`, `search_sources_by_metadata`)
- [ ] `POST /api/chat` SSE streaming endpoint
- [ ] Chat screen in app (streaming tokens, citations as tappable chips)
- [ ] Scoped chat: all library / selected collection / selected source(s)
- [ ] Session persistence (resume conversation across app restarts)
- [ ] Gemini API key configuration in settings screen

---

### Phase 2 — Reader + Annotations

**Goal**: Read sources in-app, highlight and annotate — saved as plain markdown to GDrive.

- [ ] PDF reader screen (`react-native-pdf`)
- [ ] Text selection → highlight (color picker)
- [ ] Selection → inline note (plain text input)
- [ ] Non-PDF sources: scrollable markdown renderer with inline tap-to-annotate
- [ ] Annotations sidebar: all highlights + notes for current source, by page
- [ ] Annotation types: highlight, note, question, key-claim
- [ ] Annotations serialized to `annotations.md` sidecar in GDrive (plain markdown)
- [ ] "Ask AI about this" — select text → send to chat with context pre-filled

---

### Phase 3 — Notes + Knowledge Base

**Goal**: Write plain markdown notes, link them to sources, organize everything.

- [ ] Note list screen (searchable, sorted by date / title)
- [ ] Note editor: plain markdown `TextInput` + preview toggle (`react-native-markdown-display`)
- [ ] `[[wikilink]]` mention autocomplete → links to notes or sources
- [ ] Backlinks section at bottom of each note/source
- [ ] Tags: add, remove, filter
- [ ] Collections: manually group sources + notes
- [ ] Views: list, grid (by type icon / cover), timeline (by date)
- [ ] Notes stored as `.md` in GDrive, mirrored to expo-sqlite
- [ ] Full-text search across notes + sources (SQLite FTS5)
- [ ] Quick capture from share sheet: URL → import, text → new note

---

### Phase 4 — AI Extraction

**Goal**: Automatically extract structured data from sources; custom extraction templates.

- [ ] Auto-extraction on ingestion: authors, year, journal, abstract (Gemini, LLM fallback)
- [ ] Per-source AI actions: key claims, methodology summary, open questions
- [ ] Custom extraction templates: user-defined prompts → output saved as markdown section
- [ ] Comparative summary across selected sources
- [ ] AI-generated tags suggestions
- [ ] AI agent gains new tools: `extract_structured_data`, `summarize_source`, `compare_sources`

---

### Phase 5 — Offline + GDrive Sync

**Goal**: Fully functional offline; transparent bidirectional sync to GDrive.

- [ ] All reads served from expo-sqlite + expo-file-system (local mirror)
- [ ] Write queue: mutations buffered locally, flushed to backend on reconnect
- [ ] Backend GDrive sync engine: SQLite ↔ GDrive markdown files, bidirectional
- [ ] Conflict resolution: last-write-wins (personal tool)
- [ ] Sync status per item: synced / pending / conflict
- [ ] `@react-native-community/netinfo` for connectivity awareness
- [ ] Expo Background Fetch for periodic sync when app is closed
- [ ] Sync status indicator in app header
- [ ] PWA install prompt on Expo Web

---

## Docker Compose

```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes:
      - ./data:/app/data          # SQLite DB + cached files
    env_file: .env
    depends_on: [redis]

  worker:
    build: ./backend
    command: celery -A app.workers worker --loglevel=info
    volumes:
      - ./data:/app/data
    env_file: .env
    depends_on: [redis, backend]

  redis:
    image: redis:7-alpine
    volumes: ["redis_data:/data"]

  web:                            # optional: serve Expo Web build
    image: nginx:alpine
    ports: ["3000:80"]
    volumes: ["./apps/mobile/dist:/usr/share/nginx/html:ro"]

volumes:
  redis_data:
```

---

## Environment Variables (`.env.example`)

```env
# Google OAuth + GDrive
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Gemini / Google AI
GOOGLE_GENAI_API_KEY=          # Google AI Studio key (free tier available)
GEMINI_MODEL=gemini-2.5-flash  # or gemini-2.5-pro

# Celery / Redis
REDIS_URL=redis://redis:6379/0

# App
SECRET_KEY=                    # for session signing
DATABASE_URL=sqlite:////app/data/coscienza.db
DATA_DIR=/app/data
```

---

## Open Questions (Deferred)

| # | Question | Default |
|---|---|---|
| 1 | Conflict resolution strategy for GDrive sync | Last-write-wins |
| 2 | Audio transcription: faster-whisper locally vs Gemini audio input | faster-whisper locally |
| 3 | Upgrade to Vertex AI RAG Engine later? | sqlite-vec now, swap later |
| 4 | `[[wikilink]]` scope: notes only vs notes + sources | Notes + sources |
| 5 | Annotation position format for non-PDF sources | Char offset in markdown |

---

## Success Metrics

- Import a PDF from the iOS share sheet in < 30 seconds
- Ask a question about the library and get a cited answer in < 5 seconds
- App works fully offline (flight mode)
- All data readable without the app (plain `.md` + PDF in GDrive)
- Chat answers are traceable to exact source + position

---

## Development Order

```
Phase 1: Foundation + Ingestion + Chat  ← start here (defines everything)
     ↓
Phase 2: Reader + Annotations
     ↓
Phase 3: Notes + Knowledge Base
     ↓
Phase 4: AI Extraction
     ↓
Phase 5: Offline + GDrive Sync
```
