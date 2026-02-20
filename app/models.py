"""
SQLite models: receipts, tags, and many-to-many receipt_tags.
"""
from datetime import date, datetime

from app import db


# Association table for receipt <-> tags (multiple tags per receipt)
receipt_tags = db.Table(
    "receipt_tags",
    db.Column("receipt_id", db.Integer, db.ForeignKey("receipts.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class Receipt(db.Model):
    __tablename__ = "receipts"

    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(512), nullable=False)
    original_filename = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    receipt_date = db.Column(db.Date, nullable=True)
    merchant = db.Column(db.String(256), nullable=True)
    extracted_text = db.Column(db.Text, nullable=True)

    tags = db.relationship(
        "Tag",
        secondary=receipt_tags,
        backref=db.backref("receipts", lazy="dynamic"),
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<Receipt {self.original_filename!r}>"


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Tag {self.name!r}>"
