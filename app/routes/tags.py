"""
Tags: list, create, rename, delete. Custom tags only.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.models import Tag

bp = Blueprint("tags", __name__, url_prefix="/tags")


@bp.route("/")
def index():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template("tags/index.html", tags=tags)


@bp.route("/create", methods=["POST"])
def create():
    name = (request.form.get("name") or "").strip()
    if not name:
        flash("Tag name is required.", "error")
        return redirect(url_for("tags.index"))
    if len(name) > 64:
        flash("Tag name too long.", "error")
        return redirect(url_for("tags.index"))
    existing = Tag.query.filter_by(name=name).first()
    if existing:
        flash(f"Tag «{name}» already exists.", "error")
        return redirect(url_for("tags.index"))
    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()
    flash(f"Tag «{name}» created.", "success")
    return redirect(url_for("tags.index"))


@bp.route("/<int:tag_id>/edit", methods=["GET", "POST"])
def edit(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if request.method == "GET":
        return render_template("tags/edit.html", tag=tag)
    name = (request.form.get("name") or "").strip()
    if not name:
        flash("Tag name is required.", "error")
        return redirect(url_for("tags.edit", tag_id=tag_id))
    if len(name) > 64:
        flash("Tag name too long.", "error")
        return redirect(url_for("tags.edit", tag_id=tag_id))
    existing = Tag.query.filter(Tag.name == name, Tag.id != tag_id).first()
    if existing:
        flash(f"Tag «{name}» already exists.", "error")
        return redirect(url_for("tags.edit", tag_id=tag_id))
    tag.name = name
    db.session.commit()
    flash(f"Tag renamed to «{name}».", "success")
    return redirect(url_for("tags.index"))


@bp.route("/<int:tag_id>/delete", methods=["POST"])
def delete(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    name = tag.name
    # Remove from all receipts then delete tag
    for r in list(tag.receipts):
        r.tags.remove(tag)
    db.session.delete(tag)
    db.session.commit()
    flash(f"Tag «{name}» deleted.", "success")
    return redirect(url_for("tags.index"))
