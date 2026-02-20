"""
Receipts: list, upload, detail with tag assignment, secure file serve.
"""
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_file, url_for

from app import db
from app.models import Receipt, Tag
from app.services.ocr import extract_text_and_meta
from app.services.storage import path_for_receipt, safe_save_upload

bp = Blueprint("receipts", __name__, url_prefix="/receipts")


def _allowed():
    return current_app.config["ALLOWED_EXTENSIONS"]


@bp.route("/")
def index():
    receipts = Receipt.query.order_by(Receipt.created_at.desc()).all()
    return render_template("receipts/index.html", receipts=receipts)


@bp.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("receipts/upload.html")
    if "file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("receipts.upload"))
    file = request.files["file"]
    if not file.filename:
        flash("No file selected.", "error")
        return redirect(url_for("receipts.upload"))
    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        file_path, original_filename = safe_save_upload(
            file, upload_folder, _allowed()
        )
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("receipts.upload"))
    receipt = Receipt(
        file_path=file_path,
        original_filename=original_filename,
    )
    db.session.add(receipt)
    db.session.commit()
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    try:
        meta = extract_text_and_meta(upload_folder, file_path)
        receipt.extracted_text = meta.get("extracted_text")
        receipt.receipt_date = meta.get("receipt_date")
        receipt.merchant = meta.get("merchant")
        db.session.commit()
    except Exception as e:
        current_app.logger.warning("OCR failed for receipt_id=%s", receipt.id)
        flash("Receipt saved; text extraction failed. You can still add tags and search by date.", "error")
    else:
        flash(f"Uploaded {original_filename}.", "success")
    return redirect(url_for("receipts.detail", receipt_id=receipt.id))


@bp.route("/<int:receipt_id>")
def detail(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    all_tags = Tag.query.order_by(Tag.name).all()
    return render_template(
        "receipts/detail.html",
        receipt=receipt,
        all_tags=all_tags,
    )


@bp.route("/<int:receipt_id>/tags", methods=["POST"])
def assign_tag(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    tag_id = request.form.get("tag_id", type=int)
    action = request.form.get("action")
    if tag_id is None:
        return redirect(url_for("receipts.detail", receipt_id=receipt_id))
    tag = Tag.query.get(tag_id)
    if not tag:
        return redirect(url_for("receipts.detail", receipt_id=receipt_id))
    if action == "add" and tag not in receipt.tags:
        receipt.tags.append(tag)
        db.session.commit()
        flash(f"Tag «{tag.name}» added.", "success")
    elif action == "remove" and tag in receipt.tags:
        receipt.tags.remove(tag)
        db.session.commit()
        flash(f"Tag «{tag.name}» removed.", "success")
    return redirect(url_for("receipts.detail", receipt_id=receipt_id))


@bp.route("/<int:receipt_id>/file")
def serve_file(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    path = path_for_receipt(upload_folder, receipt.file_path)
    if path is None:
        abort(404)
    return send_file(
        path,
        as_attachment=False,
        download_name=receipt.original_filename,
        mimetype=None,
    )
