from db import db
from datetime import datetime, timezone

class Enrollment(db.Model):
    __tablename__ = "Enrollment"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    cpf = db.Column(db.String, nullable=False, unique=True)
    church = db.Column(db.String, nullable=False)
    celphone = db.Column(db.String, nullable=False)
    emergency_contact = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    remedy = db.Column(db.String, nullable=False)
    hour_remedy = db.Column(db.String)
    local_proof = db.Column(db.String, nullable=False)
    payment_status = db.Column(db.String, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
