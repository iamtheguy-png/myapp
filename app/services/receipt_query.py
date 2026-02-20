"""
Shared receipt filter logic for search and export.
"""
from datetime import datetime

from sqlalchemy import func, or_

from app.models import Receipt, Tag


def build_receipt_query(tag_ids: list[int], date_from_s: str, date_to_s: str, merchant_q: str):
    """Apply filters; returns SQLAlchemy query (not executed)."""
    query = Receipt.query
    if tag_ids:
        query = query.filter(Receipt.tags.any(Tag.id.in_(tag_ids)))
    if date_from_s:
        try:
            date_from = datetime.strptime(date_from_s, "%Y-%m-%d").date()
            query = query.filter(
                or_(
                    Receipt.receipt_date >= date_from,
                    (Receipt.receipt_date.is_(None)) & (func.date(Receipt.created_at) >= date_from),
                )
            )
        except ValueError:
            pass
    if date_to_s:
        try:
            date_to = datetime.strptime(date_to_s, "%Y-%m-%d").date()
            query = query.filter(
                or_(
                    Receipt.receipt_date <= date_to,
                    (Receipt.receipt_date.is_(None)) & (func.date(Receipt.created_at) <= date_to),
                )
            )
        except ValueError:
            pass
    if merchant_q:
        safe = merchant_q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{safe}%"
        query = query.filter(
            or_(
                Receipt.merchant.ilike(pattern, escape="\\"),
                Receipt.extracted_text.ilike(pattern, escape="\\"),
            )
        )
    return query.order_by(Receipt.created_at.desc())
