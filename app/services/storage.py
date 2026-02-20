"""
Secure receipt file storage: allowlist extensions, size limits, UUID-based filenames.
Files stored outside web root; serve via app controller.
"""
import os
import uuid
from pathlib import Path

from werkzeug.datastructures import FileStorage


def allowed_extension(filename: str, allowed: set[str]) -> bool:
    """Check extension (lowercase) against allowlist after splitting once."""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in allowed


def safe_save_upload(
    file: FileStorage,
    upload_folder: str,
    allowed_extensions: set[str],
) -> tuple[str, str]:
    """
    Save uploaded file with a safe UUID-based name. Return (stored_path, original_filename).
    Raises ValueError if extension not allowed or filename invalid.
    """
    if not file or not file.filename:
        raise ValueError("No file or filename")
    original = file.filename
    if not allowed_extension(original, allowed_extensions):
        raise ValueError("File type not allowed")
    ext = original.rsplit(".", 1)[-1].lower()
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    base = Path(upload_folder)
    base.mkdir(parents=True, exist_ok=True)
    dest = base / safe_name
    file.save(str(dest))
    # Return relative path (safe_name) for DB so UPLOAD_FOLDER is portable
    return safe_name, original


def path_for_receipt(upload_folder: str, file_path: str) -> Path | None:
    """Resolve path for serving; return None if outside upload_folder or missing."""
    if not file_path or ".." in file_path or os.path.sep in file_path:
        return None
    base = Path(upload_folder).resolve()
    try:
        full = (base / file_path).resolve()
    except (OSError, ValueError):
        return None
    if not full.is_file():
        return None
    try:
        full.relative_to(base)
    except ValueError:
        return None
    return full
