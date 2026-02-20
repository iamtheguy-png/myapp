"""
Export receipts as CSV (all or with same filters as search).
"""
import csv
import io
from datetime import date

from flask import Blueprint, request, Response

from app.services.receipt_query import build_receipt_query

bp = Blueprint("export", __name__, url_prefix="/export")


def _receipt_date(r):
    return (r.receipt_date or r.created_at.date()) if r.created_at else None


def _format_date(d):
    return d.strftime("%Y-%m-%d") if d else ""


@bp.route("/receipts.csv", methods=["GET"])
def receipts_csv():
    """Export receipts as CSV. Query params: tag_id, date_from, date_to, merchant (same as search)."""
    tag_ids = request.args.getlist("tag_id", type=int)
    date_from_s = request.args.get("date_from", "").strip()
    date_to_s = request.args.get("date_to", "").strip()
    merchant_q = request.args.get("merchant", "").strip()

    query = build_receipt_query(tag_ids, date_from_s, date_to_s, merchant_q)
    receipts = query.all()

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["date", "merchant", "tags", "filename", "created_at"])
    for r in receipts:
        writer.writerow([
            _format_date(_receipt_date(r)),
            (r.merchant or ""),
            ",".join(t.name for t in r.tags),
            r.original_filename or "",
            r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
        ])
    filename = "receipts.csv"
    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
