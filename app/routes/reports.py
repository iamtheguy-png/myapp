"""
Reports: by month or by tag (counts). Output HTML view or CSV download.
"""
import csv
import io
from collections import defaultdict
from datetime import datetime

from flask import Blueprint, render_template, request, Response

from app.models import Receipt, Tag
from app.services.receipt_query import build_receipt_query

bp = Blueprint("reports", __name__, url_prefix="/reports")


def _receipt_date(r):
    if r.receipt_date:
        return r.receipt_date
    return r.created_at.date() if r.created_at else None


@bp.route("/", methods=["GET"])
def index():
    report_type = request.args.get("type", "").strip()
    date_from_s = request.args.get("date_from", "").strip()
    date_to_s = request.args.get("date_to", "").strip()
    format_type = request.args.get("format", "html").strip().lower()

    if report_type not in ("by_month", "by_tag"):
        return render_template(
            "reports/index.html",
            report_type="",
            date_from="",
            date_to="",
            by_month_rows=None,
            by_tag_rows=None,
        )

    query = build_receipt_query([], date_from_s, date_to_s, "")
    receipts = query.all()

    by_month_rows = None
    by_tag_rows = None
    if report_type == "by_month":
        buckets = defaultdict(int)
        for r in receipts:
            d = _receipt_date(r)
            if d:
                key = (d.year, d.month)
                buckets[key] += 1
        by_month_rows = [
            (f"{y}-{m:02d}", count) for (y, m), count in sorted(buckets.items())
        ]
    else:
        tag_counts = defaultdict(int)
        for r in receipts:
            for t in r.tags:
                tag_counts[t.name] += 1
        by_tag_rows = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))

    if format_type == "csv":
        out = io.StringIO()
        writer = csv.writer(out)
        if report_type == "by_month":
            writer.writerow(["month", "count"])
            for row in (by_month_rows or []):
                writer.writerow(row)
        else:
            writer.writerow(["tag", "count"])
            for row in (by_tag_rows or []):
                writer.writerow(row)
        filename = f"report_{report_type}.csv"
        return Response(
            out.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    return render_template(
        "reports/index.html",
        report_type=report_type,
        date_from=date_from_s,
        date_to=date_to_s,
        by_month_rows=by_month_rows,
        by_tag_rows=by_tag_rows,
    )
