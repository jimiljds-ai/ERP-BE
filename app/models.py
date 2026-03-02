from __future__ import annotations

from datetime import datetime
from enum import Enum

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class ProcessStage(str, Enum):
    CAD = "CAD"
    CAM = "CAM"
    TREE_MAKING = "TREE_MAKING"
    CASTING = "CASTING"
    FILING = "FILING"
    POLISHING = "POLISHING"
    PLATING = "PLATING"
    ASSEMBLING = "ASSEMBLING"


class MovementType(str, Enum):
    INFLOW = "INFLOW"
    OUTFLOW = "OUTFLOW"


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="operator")
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    movements = db.relationship("InventoryMovement", back_populates="performed_by")

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class Design(TimestampMixin, db.Model):
    __tablename__ = "designs"

    id = db.Column(db.Integer, primary_key=True)
    design_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    metal_type = db.Column(db.String(80), nullable=True)
    target_weight_grams = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    movements = db.relationship(
        "InventoryMovement",
        back_populates="design",
        cascade="all, delete-orphan",
    )


class InventoryMovement(TimestampMixin, db.Model):
    __tablename__ = "inventory_movements"

    id = db.Column(db.Integer, primary_key=True)
    design_id = db.Column(db.Integer, db.ForeignKey("designs.id"), nullable=False)
    stage = db.Column(db.Enum(ProcessStage), nullable=False)
    movement_type = db.Column(db.Enum(MovementType), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    reference_no = db.Column(db.String(80), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    movement_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    performed_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    design = db.relationship("Design", back_populates="movements")
    performed_by = db.relationship("User", back_populates="movements")

    @property
    def signed_quantity(self) -> float:
        return self.quantity if self.movement_type == MovementType.INFLOW else -self.quantity
