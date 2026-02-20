"""
OCR for receipts: Tesseract on images; PDF via PyMuPDF (text) or pdf2image + Tesseract (scanned).
Optional heuristics to infer receipt_date and merchant from extracted text.
"""
import re
from datetime import date
from pathlib import Path

# Optional deps: fail gracefully if not installed
try:
    import pytesseract
    from PIL import Image
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    import pymupdf
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


def _full_path(upload_folder: str, file_path: str) -> Path:
    return Path(upload_folder) / file_path


def _extract_text_image(path: Path) -> str:
    if not PYTESSERACT_AVAILABLE:
        return ""
    try:
        img = Image.open(path)
        if img.mode not in ("L", "RGB", "RGBA"):
            img = img.convert("RGB")
        return pytesseract.image_to_string(img) or ""
    except Exception:
        return ""


def _extract_text_pdf(path: Path, upload_folder: str) -> str:
    text_from_pymupdf = ""
    if PYMUPDF_AVAILABLE:
        try:
            doc = pymupdf.open(path)
            parts = []
            for page in doc:
                parts.append(page.get_text())
            doc.close()
            text_from_pymupdf = "\n".join(parts).strip()
        except Exception:
            pass
    if len(text_from_pymupdf) >= 30:
        return text_from_pymupdf
    if PDF2IMAGE_AVAILABLE and PYTESSERACT_AVAILABLE:
        try:
            images = convert_from_path(path, dpi=150)
            parts = []
            for img in images:
                parts.append(pytesseract.image_to_string(img))
            return "\n".join(parts).strip()
        except Exception:
            pass
    return text_from_pymupdf


def _parse_date_from_text(text: str) -> date | None:
    """Try to find a date in text; return first plausible receipt-style date."""
    if not text:
        return None
    # ISO
    m = re.search(r"\b(20\d{2})-(\d{1,2})-(\d{1,2})\b", text)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    # US style MM/DD/YYYY or MM-DD-YYYY
    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](20\d{2})\b", text)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        except ValueError:
            pass
    # DD.MM.YYYY or DD/MM/YYYY
    m = re.search(r"\b(\d{1,2})[./](\d{1,2})[./](20\d{2})\b", text)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass
    return None


def _parse_merchant_from_text(text: str) -> str | None:
    """Heuristic: first line that looks like a merchant name (not a date, not mostly digits)."""
    if not text:
        return None
    date_pattern = re.compile(
        r"^(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]20\d{2})$"
    )
    for line in text.splitlines():
        line = line.strip()
        if not line or len(line) < 2 or len(line) > 200:
            continue
        if date_pattern.match(line):
            continue
        if re.match(r"^[\d\s.,$€£]+$", line):
            continue
        return line[:256]
    return None


def extract_text_and_meta(
    upload_folder: str,
    file_path: str,
) -> dict:
    """
    Run OCR and optional parsing. Returns dict with keys:
    extracted_text, receipt_date, merchant (all optional).
    """
    full = _full_path(upload_folder, file_path)
    if not full.is_file():
        return {"extracted_text": None, "receipt_date": None, "merchant": None}
    ext = full.suffix.lower()
    text = ""
    if ext == ".pdf":
        text = _extract_text_pdf(full, upload_folder)
    elif ext in (".jpg", ".jpeg", ".png"):
        text = _extract_text_image(full)
    text = text.strip() or None
    receipt_date = _parse_date_from_text(text) if text else None
    merchant = _parse_merchant_from_text(text) if text else None
    return {
        "extracted_text": text,
        "receipt_date": receipt_date,
        "merchant": merchant,
    }
