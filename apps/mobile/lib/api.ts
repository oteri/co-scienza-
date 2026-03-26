const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${options.method ?? 'GET'} ${path} → ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  // Sources
  getSources: () => request<Source[]>('/api/sources/'),
  getSource: (id: string) => request<Source>(`/api/sources/${id}`),
  createSource: (body: SourceCreate) =>
    request<Source>('/api/sources/', { method: 'POST', body: JSON.stringify(body) }),
  deleteSource: (id: string) =>
    request<void>(`/api/sources/${id}`, { method: 'DELETE' }),

  // Notes
  getNotes: () => request<Note[]>('/api/notes/'),
  getNote: (id: string) => request<Note>(`/api/notes/${id}`),
  createNote: (body: { title: string; content: string }) =>
    request<Note>('/api/notes/', { method: 'POST', body: JSON.stringify(body) }),
  updateNote: (id: string, body: { title?: string; content?: string }) =>
    request<Note>(`/api/notes/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  deleteNote: (id: string) =>
    request<void>(`/api/notes/${id}`, { method: 'DELETE' }),

  // Chat (SSE — handled separately in useChat hook)
  chatUrl: () => `${BASE_URL}/api/chat/`,
};

// ── Types (mirror backend Pydantic models) ───────────────────────────────────

export interface Source {
  id: string;
  title: string | null;
  type: string;
  url: string | null;
  status: string;
  source_metadata: Record<string, unknown> | null;
}

export interface SourceCreate {
  type: string;
  url?: string;
  doi?: string;
  arxiv_id?: string;
  pubmed_id?: string;
  text?: string;
  title?: string;
}

export interface Note {
  id: string;
  title: string | null;
  content: string | null;
}
