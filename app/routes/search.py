"""
Search receipts by tags (OR), date range, and merchant (substring in merchant or extracted_text).
"""
from flask import Blueprint, render_template, request

from app.models import Tag
from app.services.receipt_query import build_receipt_query

bp = Blueprint("search", __name__, url_prefix="/search")


@bp.route("/", methods=["GET"])
def index():
    tag_ids = request.args.getlist("tag_id", type=int)
    date_from_s = request.args.get("date_from", "").strip()
    date_to_s = request.args.get("date_to", "").strip()
    merchant_q = request.args.get("merchant", "").strip()

    query = build_receipt_query(tag_ids, date_from_s, date_to_s, merchant_q)
    receipts = query.all()
    all_tags = Tag.query.order_by(Tag.name).all()
    return render_template(
        "search/index.html",
        receipts=receipts,
        all_tags=all_tags,
        selected_tag_ids=tag_ids,
        date_from=date_from_s,
        date_to=date_to_s,
        merchant=merchant_q,
    )
