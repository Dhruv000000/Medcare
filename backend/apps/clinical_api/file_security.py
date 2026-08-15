from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

MAX_UPLOAD_SIZE = 5 * 1024 * 1024
_ALLOWED = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".txt": "text/plain",
}
_PDF_SIGNATURE = b"%PDF-"
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_JPEG_SIGNATURE = b"\xff\xd8\xff"
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_original_filename(name: str) -> str:
    """Return a short, basename-only display name with no path/control characters."""
    raw = Path(str(name or "attachment")).name
    raw = _CONTROL_CHARS.sub("", raw)
    raw = _UNSAFE_FILENAME_CHARS.sub("_", raw).strip("._")
    if not raw:
        raw = "attachment"
    return raw[:180]


def _read_uploaded(upload: UploadedFile) -> bytes:
    try:
        upload.seek(0)
        data = upload.read(MAX_UPLOAD_SIZE + 1)
        upload.seek(0)
        return data
    except Exception as exc:  # pragma: no cover - defensive boundary
        raise ValidationError("The uploaded file could not be read safely.") from exc


def _signature_matches(extension: str, content: bytes) -> bool:
    if extension == ".pdf":
        return content.startswith(_PDF_SIGNATURE)
    if extension == ".png":
        return content.startswith(_PNG_SIGNATURE)
    if extension in {".jpg", ".jpeg"}:
        return content.startswith(_JPEG_SIGNATURE)
    if extension == ".txt":
        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            return False
        return True
    return False


def validate_uploaded_file(upload: UploadedFile) -> dict[str, object]:
    """Validate one clinical attachment and return safe metadata for persistence."""
    if not upload or not getattr(upload, "name", None):
        raise ValidationError("A file is required.")

    name = sanitize_original_filename(upload.name)
    extension = Path(name).suffix.lower()
    expected_mime = _ALLOWED.get(extension)
    supplied_mime = (getattr(upload, "content_type", "") or "").lower().split(";", 1)[0].strip()
    size = int(getattr(upload, "size", 0) or 0)

    if extension not in _ALLOWED:
        raise ValidationError("This file type is not supported.")
    if size <= 0 or size > MAX_UPLOAD_SIZE:
        raise ValidationError("The uploaded file exceeds the permitted size.")
    if supplied_mime and supplied_mime != expected_mime:
        raise ValidationError("The file content type does not match its extension.")

    content = _read_uploaded(upload)
    if len(content) > MAX_UPLOAD_SIZE:
        raise ValidationError("The uploaded file exceeds the permitted size.")
    if not _signature_matches(extension, content):
        raise ValidationError("The file signature does not match its extension.")

    return {
        "original_name": name,
        "content_type": expected_mime,
        "size": size,
    }


def protected_upload_to(instance, filename: str) -> str:
    """Generate a non-guessable relative path; the file remains under MEDIA_ROOT."""
    extension = Path(sanitize_original_filename(filename)).suffix.lower()
    return f"protected/clinical/{uuid4().hex}{extension}"
