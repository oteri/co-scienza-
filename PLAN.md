# co-scienza — Product Plan

> A personal knowledge management system combining the best of Zotero, NotebookLM, Obsidian, and Notion.

---

## Vision

co-scienza is a **personal, offline-first knowledge base** for capturing, reading, annotating, and querying any type of source — papers, web pages, videos, audio, notes — with AI as a built-in layer for extraction and querying.

Your data lives **on your terms**: stored as readable files (markdown + PDFs) synced to Google Drive, with a local index for fast search and AI.

---

## Core Principles

1. **Data ownership** — all content stored as markdown + PDFs on Google Drive. No vendor lock-in.
2. **Offline-first** — the app is fully functional without internet; GDrive sync happens in the background.
3. **AI as a layer, not a gate** — AI features enhance the experience but are optional and pluggable.
4. **Mobile-ready** — PWA, accessible from phone with the same feature set.
5. **Personal tool** — no multi-tenancy, no sharing, no auth complexity beyond GDrive OAuth.

---

## Tech Stack

### Frontend
- **Next.js 14+** (App Router, React 18) — web app + API routes in one
- **PWA** (via `next-pwa` + service worker) — offline support + mobile installability
- **TailwindCSS** — styling
- **TipTap** (or **BlockNote**) — block-based editor (like Notion)
- **react-pdf / PDF.js** — in-browser PDF rendering and annotation

### Backend (Next.js API Routes + Node workers)
- **SQLite** (via **Drizzle ORM**) — metadata, annotations, tags, full-text search
- **sqlite-vec** or **LanceDB** — vector embeddings stored alongside content
- **BullMQ** (or custom job queue) — background ingestion, embedding, sync jobs
- **Google Drive API** — primary file storage (markdown + PDFs)
- **NextAuth.js** — Google OAuth for GDrive access token

### AI Layer (pluggable)
- **Vercel AI SDK** — unified interface for multiple providers
- Supported providers: **Anthropic**, **OpenAI**, **Google Gemini**, **Ollama** (local)
- Embeddings: provider-configurable (OpenAI `text-embedding-3-small`, Ollama `nomic-embed-text`, etc.)

### Ingestion Tools
- **Readability.js** — extract readable content from URLs
- **CrossRef / arXiv / PubMed APIs** — academic metadata + PDF links
- **youtube-transcript** — YouTube transcript fetching
- **Whisper** (via Ollama or OpenAI) — audio transcription
- **Tesseract.js** or multimodal LLM — image OCR/description
- **Unpaywall / Sci-Hub fallback** — open-access PDF resolution

### Deployment
- **Self-hosted** (Docker Compose recommended)
- SQLite DB + file cache on server volume
- GDrive as the durable cloud storage layer

---

## Data Model

```
Source
  id, title, type, url, doi, arxiv_id
  file_path (GDrive path), local_cache_path
  status: pending | processing | ready | failed
  metadata: JSON (authors, year, journal, abstract, duration, etc.)
  created_at, updated_at, synced_at

Annotation
  id, source_id
  type: highlight | note | comment
  content (markdown)
  position: JSON (page, rects for PDF; char offset for text)
  color, tags[]
  created_at

Note
  id, title, content (markdown blocks)
  file_path (GDrive path)
  tags[], links[] (bidirectional)
  created_at, updated_at

Tag
  id, name, color
  (applies to Source, Note, Annotation)

Collection / Library
  id, name, description
  source_ids[], note_ids[]

Embedding
  id, entity_id, entity_type (source | note | annotation | chunk)
  chunk_text, vector
  model_id

SyncLog
  id, entity_id, entity_type, action, gdrive_file_id
  synced_at, status
```

---

## GDrive File Structure

```
GDrive: /co-scienza/
  sources/
    {year}/
      {slug}/
        source.pdf          ← original file
        metadata.json       ← structured metadata
        annotations.md      ← all highlights + notes for this source
        chunks/             ← text chunks (for embedding traceability)
  notes/
    {slug}.md               ← standalone notes
  collections/
    {name}.json             ← collection definitions
  config.json               ← app settings (AI provider, sync prefs)
```

---

## Feature Phases

### Phase 1 — Foundation + Source Ingestion (MVP)

**Goal**: Import any content into the system, extract text, store in GDrive.

#### Setup
- [ ] Next.js project scaffolding with TypeScript
- [ ] SQLite + Drizzle ORM schema
- [ ] Google OAuth + GDrive API integration
- [ ] GDrive folder structure initialization
- [ ] Background job queue for async processing

#### Importers
- [ ] **PDF upload** — drag & drop or file picker → extract text (pdf-parse), store in GDrive
- [ ] **URL** — fetch → Readability.js → markdown + screenshot → GDrive
- [ ] **DOI** — CrossRef API → metadata + PDF link → download → GDrive
- [ ] **arXiv ID / URL** — arXiv API → metadata + PDF → GDrive
- [ ] **PubMed ID** — NCBI API → metadata + PDF (Unpaywall fallback)
- [ ] **YouTube URL** — transcript via `youtube-transcript` → markdown → GDrive
- [ ] **Audio file** — upload → Whisper transcription → markdown → GDrive
- [ ] **Image** — upload → OCR or multimodal description → markdown → GDrive
- [ ] **Plain text / markdown paste** — direct input

#### Source Library View
- [ ] List view with search and filters (type, tag, date, status)
- [ ] Grid view with cover images / thumbnails
- [ ] Source detail page (metadata, status, quick actions)
- [ ] Import status indicators (queued → processing → ready)

---

### Phase 2 — PDF Reader + Annotations

**Goal**: Read papers in-app with highlights and notes, saved back to GDrive.

- [ ] In-app PDF viewer (PDF.js, page-by-page rendering)
- [ ] Text selection → highlight (color picker)
- [ ] Selected text → inline note (Markdown editor popup)
- [ ] Sidebar: all annotations for current document, sorted by page
- [ ] Annotation types: highlight, note, question, key-claim
- [ ] Export annotations as markdown summary
- [ ] Keyboard shortcuts for annotation workflow
- [ ] Annotations saved to `annotations.md` sidecar in GDrive
- [ ] Mobile-friendly reading layout (scrollable, touch-friendly)

---

### Phase 3 — Knowledge Base + Editor

**Goal**: Write notes, link them to sources and each other, organize into collections.

- [ ] Block-based editor (paragraphs, headings, lists, code, quotes, embeds)
- [ ] Markdown shortcuts (e.g., `##`, `- `, `[[`)
- [ ] `[[wikilink]]` syntax with autocomplete → bidirectional links
- [ ] Backlinks panel per note/source
- [ ] Tags system (hierarchical optional)
- [ ] Collections / Libraries (manual grouping of sources + notes)
- [ ] Multiple views: list, grid, kanban (by tag/status), timeline (by date)
- [ ] Notes stored as `.md` files in GDrive
- [ ] Full-text search across sources + notes (SQLite FTS5)
- [ ] Quick capture (global shortcut or share-sheet on mobile)

---

### Phase 4 — AI Querying + Extraction

**Goal**: Ask questions over your knowledge base, extract structured data, get summaries.

#### Embedding Pipeline
- [ ] Chunk sources + notes into segments (configurable size)
- [ ] Embed chunks on ingestion (background job)
- [ ] Store vectors in sqlite-vec / LanceDB
- [ ] Re-embed on content change

#### RAG Query Interface
- [ ] Chat interface: ask questions, get answers with source citations
- [ ] Semantic search (vector + keyword hybrid)
- [ ] Scoped queries: "search only in this collection" or "from papers after 2022"
- [ ] Answer with inline references (click → open source at location)

#### Structured Extraction (per source)
- [ ] Auto-extract: authors, year, journal, abstract (if not from API)
- [ ] Key claims / contributions (LLM extraction)
- [ ] Methodology summary
- [ ] Open questions / limitations
- [ ] Related works (linked to other sources in your library)
- [ ] Custom extraction templates (user-defined fields)

#### AI Summaries
- [ ] One-click summary per source
- [ ] Comparative summary across selected sources
- [ ] "Explain this to me like I'm a novice" mode

#### Provider Configuration
- [ ] Settings page: choose AI provider + model
- [ ] Support: Anthropic Claude, OpenAI GPT, Google Gemini, Ollama (local)
- [ ] API key management (stored locally, never server-side)
- [ ] Embedding model separate from chat model config

---

### Phase 5 — Offline + Sync

**Goal**: Full offline functionality with transparent GDrive sync.

- [ ] Service worker (PWA) for offline asset caching
- [ ] IndexedDB local mirror for offline reads (sources, notes, annotations)
- [ ] Sync queue: buffer writes offline, flush when back online
- [ ] GDrive sync engine:
  - [ ] Local SQLite ↔ GDrive files bidirectional sync
  - [ ] Conflict detection (last-write-wins or manual resolution)
  - [ ] Sync status indicators (synced / pending / conflict)
- [ ] Installable on mobile (PWA add-to-homescreen)
- [ ] Background sync via Service Worker (when app is closed)
- [ ] Offline indicator + sync status in UI

---

## Open Questions (Decisions Needed)

These are unresolved decisions that will affect implementation. Will need your input when we reach each phase:

1. **Editor choice**: TipTap (more customizable, larger bundle) vs. BlockNote (faster to set up, opinionated) — lean toward BlockNote for speed.
2. **Vector storage**: sqlite-vec (zero-dependency, embedded) vs. LanceDB (more scalable) — lean toward sqlite-vec for simplicity.
3. **PDF annotation storage format**: sidecar `.md` file vs. embedded PDF annotations — sidecar is simpler and human-readable.
4. **Offline sync conflict strategy**: last-write-wins vs. 3-way merge — last-write-wins is simpler for a personal tool.
5. **Audio transcription**: Whisper via OpenAI API (easy) vs. Whisper.cpp locally (private, slower) — make it provider-configurable.
6. **Mobile quick capture**: PWA share-sheet (limited but no native code) vs. native app later — start with PWA share-sheet.

---

## Success Metrics (Personal)

- Can import a PDF, read it, highlight it, and ask questions about it in < 5 minutes
- Can capture a URL from mobile in < 30 seconds
- Works fully offline on a flight
- All data readable without the app (plain markdown + PDFs in GDrive)
- AI querying returns cited, accurate answers from my library

---

## Development Order (Recommended)

```
Phase 1 (Ingestion)  →  Phase 2 (PDF Reader)  →  Phase 3 (Editor/KB)
       ↓
Phase 4 (AI)  →  Phase 5 (Sync/PWA)
```

Start with Phase 1 since it defines the data model and GDrive integration that everything else builds on.
