"""
Thin Google Drive API wrapper.
Handles folder creation, file upload, and metadata reads.
"""

import io
import json

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials

from app.core.config import settings

MIME_FOLDER = "application/vnd.google-apps.folder"
MIME_MARKDOWN = "text/markdown"
MIME_JSON = "application/json"
MIME_PDF = "application/pdf"


class GDriveClient:
    def __init__(self, credentials: Credentials):
        self._service = build("drive", "v3", credentials=credentials, cache_discovery=False)

    def _files(self):
        return self._service.files()

    def get_or_create_folder(self, name: str, parent_id: str | None = None) -> str:
        """Return folder ID, creating it if it doesn't exist."""
        query = f"name='{name}' and mimeType='{MIME_FOLDER}' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        results = self._files().list(q=query, fields="files(id)").execute()
        files = results.get("files", [])
        if files:
            return files[0]["id"]
        metadata = {"name": name, "mimeType": MIME_FOLDER}
        if parent_id:
            metadata["parents"] = [parent_id]
        folder = self._files().create(body=metadata, fields="id").execute()
        return folder["id"]

    def upload_text(self, name: str, content: str, parent_id: str, mime: str = MIME_MARKDOWN) -> str:
        """Upload or update a text file. Returns the file ID."""
        query = f"name='{name}' and '{parent_id}' in parents and trashed=false"
        results = self._files().list(q=query, fields="files(id)").execute()
        existing = results.get("files", [])
        media = MediaIoBaseUpload(io.BytesIO(content.encode()), mimetype=mime)
        if existing:
            file = self._files().update(
                fileId=existing[0]["id"], media_body=media, fields="id"
            ).execute()
        else:
            file = self._files().create(
                body={"name": name, "parents": [parent_id]},
                media_body=media,
                fields="id",
            ).execute()
        return file["id"]

    def upload_bytes(self, name: str, content: bytes, parent_id: str, mime: str = MIME_PDF) -> str:
        """Upload binary file (e.g. PDF). Returns file ID."""
        media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mime)
        file = self._files().create(
            body={"name": name, "parents": [parent_id]},
            media_body=media,
            fields="id",
        ).execute()
        return file["id"]

    def upload_json(self, name: str, data: dict, parent_id: str) -> str:
        return self.upload_text(name, json.dumps(data, indent=2), parent_id, mime=MIME_JSON)

    def init_root_structure(self) -> dict[str, str]:
        """Create /co-scienza/{sources,notes,collections}/ and return folder IDs."""
        root_id = self.get_or_create_folder(settings.GDRIVE_ROOT_FOLDER_NAME)
        sources_id = self.get_or_create_folder("sources", root_id)
        notes_id = self.get_or_create_folder("notes", root_id)
        collections_id = self.get_or_create_folder("collections", root_id)
        return {
            "root": root_id,
            "sources": sources_id,
            "notes": notes_id,
            "collections": collections_id,
        }
