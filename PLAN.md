# co-scienza — Product Plan

> A personal, offline-first knowledge management system combining the best of Zotero,
> NotebookLM, Obsidian, and Notion — built mobile-first with Expo + React Native.

---

## Vision

co-scienza is a **personal, offline-first knowledge base** for capturing, reading, annotating,
and querying any type of source — papers, web pages, videos, audio, notes — with AI as a
built-in layer for extraction and querying.

Your data lives **on your terms**: stored as readable files (markdown + PDFs) synced to
Google Drive, with a local index for fast search and AI.

---

## Core Principles

1. **Data ownership** — all content stored as markdown + PDFs on Google Drive. No vendor lock-in.
2. **Offline-first** — fully functional without internet; GDrive sync happens in the background.
3. **AI as a layer, not a gate** — AI features are optional and pluggable (Anthropic, OpenAI, Gemini, Ollama).
4. **Mobile-first** — designed for iOS/Android first, accessible on web via Expo Web.
5. **Personal tool** — no multi-tenancy, no sharing complexity. Just you and your knowledge.

---

## Tech Stack

### Frontend — Expo (React Native)
| Concern | Choice | Notes |
|---|---|---|
| Framework | **Expo SDK** (React Native) | iOS, Android, Web (Expo Web) |
| Navigation | **Expo Router** | File-based routing, works on web too |
| Editor | **TenTap (`@10play/tentap-editor`)** | TipTap-based block editor for RN — supports paragraphs, headings, lists, code, quotes, bold/italic |
| PDF viewer | **react-native-pdf** | Mobile; web fallback via iframe or PDF.js |
| Styling | **NativeWind** (Tailwind for RN) | Consistent design system cross-platform |
| State | **Zustand** | Lightweight, works offline-first |
| Data sync / cache | **expo-sqlite** + **TanStack Query** | Local SQLite mirror; query cache |
| Offline storage | **expo-sqlite** (structured) + **expo-file-system** (blobs) | PDFs, markdown cached locally |
| PWA / Web | **Expo Web** | Same codebase, browser-accessible |

### Backend — Python FastAPI
| Concern | Choice | Notes |
|---|---|---|
| Framework | **FastAPI** | Async, typed, fast |
| Database | **SQLite** via **SQLAlchemy** + **Alembic** | Single-file DB, perfect for self-hosted solo use |
| Vector store | **sqlite-vec** | Embedded vectors in SQLite — zero extra services |
| Background jobs | **Celery** + **Redis** | Or `asyncio` task queue if Redis feels heavy |
| GDrive sync | **google-api-python-client** | Read/write files, manage folder structure |
| AI / LLM | **LiteLLM** | Single interface for Anthropic, OpenAI, Gemini, Ollama |
| Embeddings | **LiteLLM** embedding endpoint | Pluggable: OpenAI, Ollama nomic-embed, etc. |
| PDF text extraction | **pdfminer.six** / **pypdf** | Pure Python, no binary deps |
| Web scraping | **httpx** + **trafilatura** | URL → clean article text |
| YouTube | **youtube-transcript-api** | Fetch transcripts by URL/ID |
| Audio | **faster-whisper** or OpenAI Whisper API | Local or cloud transcription |
| OCR / images | **pytesseract** or multimodal LLM | Image → text |
| Academic metadata | **httpx** + CrossRef / arXiv / PubMed APIs | DOI, arXiv ID, PubMed ID resolution |

### Infrastructure
| Concern | Choice |
|---|---|
| Containerization | **Docker Compose** |
| Reverse proxy | **Caddy** (optional, for HTTPS) |
| File serving | FastAPI static files or Caddy |

---

## Monorepo Structure

```
co-scienza/
├── apps/
│   └── mobile/               ← Expo app (iOS, Android, Web)
│       ├── app/              ← Expo Router screens
│       ├── components/
│       ├── hooks/
│       ├── store/            ← Zustand stores
│       └── lib/              ← API client, sync logic
├── backend/
│   ├── app/
│   │   ├── api/              ← FastAPI routers
│   │   ├── models/           ← SQLAlchemy models
│   │   ├── services/
│   │   │   ├── ingest/       ← importers per source type
│   │   │   ├── ai/           ← LLM, embeddings, RAG
│   │   │   └── gdrive/       ← GDrive sync engine
│   │   ├── workers/          ← Celery tasks
│   │   └── main.py
│   ├── alembic/              ← DB migrations
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
│           ├── metadata.json       ← structured metadata
│           ├── content.md          ← extracted/scraped text
│           └── annotations.md      ← highlights + notes
├── notes/
│   └── {slug}.md                   ← standalone notes
├── collections/
│   └── {name}.json                 ← collection definitions
└── config.json                     ← app config (AI provider, sync prefs)
```

---

## Data Model (SQLite — backend)

```sql
-- Sources: any imported content
CREATE TABLE sources (
  id TEXT PRIMARY KEY,
  title TEXT,
  type TEXT,        -- pdf | url | doi | arxiv | youtube | audio | image | note
  url TEXT,
  doi TEXT,
  arxiv_id TEXT,
  gdrive_file_id TEXT,
  local_cache_path TEXT,
  status TEXT,      -- pending | processing | ready | failed
  metadata JSON,    -- authors, year, journal, abstract, duration, etc.
  created_at DATETIME,
  updated_at DATETIME,
  synced_at DATETIME
);

-- Annotations on sources (highlights, notes, questions)
CREATE TABLE annotations (
  id TEXT PRIMARY KEY,
  source_id TEXT REFERENCES sources(id),
  type TEXT,        -- highlight | note | comment | question | key-claim
  content TEXT,     -- markdown
  position JSON,    -- {page, rects} for PDF; {start, end} for text
  color TEXT,
  created_at DATETIME
);

-- Standalone notes (block-based, markdown)
CREATE TABLE notes (
  id TEXT PRIMARY KEY,
  title TEXT,
  content TEXT,     -- markdown / TenTap JSON blocks
  gdrive_file_id TEXT,
  created_at DATETIME,
  updated_at DATETIME
);

-- Tags (apply to sources, notes, annotations)
CREATE TABLE tags (id TEXT PRIMARY KEY, name TEXT, color TEXT);
CREATE TABLE source_tags (source_id TEXT, tag_id TEXT);
CREATE TABLE note_tags (note_id TEXT, tag_id TEXT);

-- Bidirectional links between notes / sources
CREATE TABLE links (
  from_id TEXT, from_type TEXT,
  to_id TEXT,   to_type TEXT
);

-- Collections / Libraries
CREATE TABLE collections (
  id TEXT PRIMARY KEY, name TEXT, description TEXT, created_at DATETIME
);
CREATE TABLE collection_items (
  collection_id TEXT, item_id TEXT, item_type TEXT -- source | note
);

-- Vector embeddings for RAG
CREATE TABLE embeddings (
  id TEXT PRIMARY KEY,
  entity_id TEXT, entity_type TEXT,   -- source | note | annotation
  chunk_text TEXT,
  chunk_index INTEGER,
  model_id TEXT,
  vector BLOB  -- stored via sqlite-vec
);

-- GDrive sync log
CREATE TABLE sync_log (
  id TEXT PRIMARY KEY,
  entity_id TEXT, entity_type TEXT,
  action TEXT,      -- create | update | delete
  gdrive_file_id TEXT,
  status TEXT,      -- pending | done | conflict | failed
  synced_at DATETIME
);
```

---

## Feature Phases

### Phase 1 — Foundation + Source Ingestion (MVP)

**Goal**: Import any content, extract text, store locally + sync to GDrive.

#### Backend setup
- [ ] FastAPI project with SQLAlchemy + Alembic migrations
- [ ] SQLite DB initialization
- [ ] Google OAuth flow → store access/refresh token
- [ ] GDrive folder structure initialization on first run
- [ ] Background job queue (Celery + Redis, or asyncio)
- [ ] Docker Compose: `backend` + `redis` services

#### Expo app setup
- [ ] Expo project with Expo Router
- [ ] NativeWind configuration
- [ ] Zustand store setup
- [ ] API client (httpx/fetch wrapper pointing to backend)
- [ ] expo-sqlite local mirror schema

#### Importers (backend services)
- [ ] **PDF upload** — extract text (pypdf), store file in GDrive, index in SQLite
- [ ] **URL** — fetch → trafilatura → clean markdown → GDrive
- [ ] **DOI** — CrossRef API → metadata + Unpaywall PDF link → download → GDrive
- [ ] **arXiv ID / URL** — arXiv API → metadata + PDF → GDrive
- [ ] **PubMed ID** — NCBI API → metadata + PDF fallback
- [ ] **YouTube URL** — youtube-transcript-api → markdown → GDrive
- [ ] **Audio file** — faster-whisper or OpenAI Whisper API → transcript → GDrive
- [ ] **Image** — pytesseract OCR or multimodal LLM → description → GDrive
- [ ] **Plain text / markdown paste** — direct input → GDrive

#### Source Library (mobile UI)
- [ ] Source list screen (searchable, filterable by type/tag/status)
- [ ] Source grid view (cover image / type icon)
- [ ] Import sheet (bottom sheet with source type picker)
- [ ] Import status: queued → processing → ready (live polling or SSE)
- [ ] Source detail screen (metadata, status, quick actions)

---

### Phase 2 — PDF Reader + Annotations

**Goal**: Read sources in-app, highlight, add notes — saved back to GDrive.

- [ ] PDF reader screen using `react-native-pdf`
- [ ] Text selection → highlight (color picker bottom sheet)
- [ ] Selection → inline note (markdown input)
- [ ] Annotation sidebar: all highlights/notes for current document by page
- [ ] Annotation types: highlight, note, question, key-claim
- [ ] Annotations serialized to `annotations.md` sidecar in GDrive
- [ ] Keyboard shortcuts on web (Expo Web)
- [ ] Non-PDF sources: rendered markdown reader with inline annotation

---

### Phase 3 — Knowledge Base + Editor

**Goal**: Write notes, link them to sources and each other, organize everything.

- [ ] Note editor screen using **TenTap** blocks:
  - Paragraph, heading (H1–H3), bullet list, numbered list, blockquote, code block
  - Bold, italic, underline, strikethrough, inline code
- [ ] `[[wikilink]]` autocomplete → link to other notes or sources
- [ ] Backlinks panel per note/source
- [ ] Tags system (add, remove, filter by tag)
- [ ] Collections: group sources + notes manually
- [ ] Views: list, grid, kanban (by tag or status), timeline (by date)
- [ ] Notes saved as `.md` in GDrive + mirrored to expo-sqlite
- [ ] Full-text search across sources + notes (SQLite FTS5 on backend)
- [ ] Quick capture: share-sheet integration on iOS/Android (Expo Share Intent)

---

### Phase 4 — AI Querying + Extraction

**Goal**: Ask questions, get cited answers, extract structured data automatically.

#### Embedding pipeline
- [ ] Chunking strategy: sliding window, configurable size
- [ ] Embed chunks on ingestion (background Celery task)
- [ ] sqlite-vec for vector storage alongside metadata DB
- [ ] Re-embed on content update

#### RAG chat interface
- [ ] Chat screen: ask questions, stream answers via SSE
- [ ] Answers include source citations (tap → open source at location)
- [ ] Scoped queries: all library / selected collection / selected sources
- [ ] Hybrid search: vector similarity + FTS keyword

#### Structured extraction (per source)
- [ ] Auto-extract on ingestion: authors, year, journal, abstract (LLM fallback)
- [ ] Key claims / contributions
- [ ] Methodology summary
- [ ] Open questions / limitations
- [ ] Custom extraction templates (user-defined JSON schema → LLM extraction)

#### AI summaries
- [ ] One-tap summary per source
- [ ] Comparative summary across selected sources
- [ ] "Explain to me simply" mode

#### AI provider configuration
- [ ] Settings screen: provider + model picker
- [ ] Supported: Anthropic Claude, OpenAI GPT, Google Gemini, Ollama (local URL)
- [ ] API keys stored in `expo-secure-store` (encrypted on device)
- [ ] Separate config for chat model vs. embedding model
- [ ] Test connection button

---

### Phase 5 — Offline + GDrive Sync

**Goal**: Fully functional offline; transparent sync to GDrive when connected.

- [ ] Local-first reads: all content served from expo-sqlite + expo-file-system
- [ ] Write queue: mutations buffered locally, flushed to backend on reconnect
- [ ] Backend GDrive sync engine:
  - [ ] Bidirectional: local SQLite ↔ GDrive markdown files
  - [ ] Conflict detection: compare `updated_at` timestamps
  - [ ] Conflict resolution: last-write-wins (personal tool default)
  - [ ] Sync status per item: synced / pending / conflict
- [ ] Network awareness: `@react-native-community/netinfo`
- [ ] Background sync: Expo Background Fetch for periodic sync when app is closed
- [ ] Sync status indicator in app header
- [ ] PWA install prompt on web (Expo Web)

---

## Docker Compose Services

```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes:
      - ./data/db:/app/data       # SQLite + cached files
    environment:
      - GOOGLE_CLIENT_ID
      - GOOGLE_CLIENT_SECRET
      - REDIS_URL=redis://redis:6379
    depends_on: [redis]

  worker:
    build: ./backend
    command: celery -A app.workers worker
    volumes:
      - ./data/db:/app/data
    depends_on: [redis, backend]

  redis:
    image: redis:7-alpine
    volumes: ["redis_data:/data"]

  # Optional: serve Expo web build
  web:
    image: nginx:alpine
    ports: ["3000:80"]
    volumes: ["./apps/mobile/dist:/usr/share/nginx/html:ro"]

volumes:
  redis_data:
```

---

## Open Questions (Deferred Decisions)

| # | Question | Default |
|---|---|---|
| 1 | PDF annotation format: sidecar `.md` vs embedded PDF annotations | Sidecar `.md` (human-readable) |
| 2 | Audio transcription: faster-whisper locally vs OpenAI API | User-configurable (same as AI provider) |
| 3 | Background job queue: Celery+Redis vs pure asyncio | Celery+Redis (more robust for ingestion) |
| 4 | TenTap storage format: HTML vs JSON blocks vs markdown | Markdown (GDrive-friendly) |
| 5 | `[[wikilink]]` resolution scope: notes only vs notes+sources | Notes + sources |
| 6 | Conflict resolution strategy | Last-write-wins |

---

## Success Metrics

- Import a PDF, read it, highlight it, ask questions about it in < 5 minutes
- Capture a URL from iOS share-sheet in < 30 seconds
- App works fully offline (flight mode)
- All data readable without the app (plain markdown + PDFs in GDrive)
- AI answers are cited and traceable to source location

---

## Development Order

```
Phase 1: Foundation + Ingestion   (defines data model + GDrive + Docker)
     ↓
Phase 2: PDF Reader + Annotations  (core reading workflow)
     ↓
Phase 3: Knowledge Base + Editor   (note-taking + organization)
     ↓
Phase 4: AI Layer                  (query + extraction)
     ↓
Phase 5: Offline + Sync            (resilience + mobile polish)
```
