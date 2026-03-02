from __future__ import annotations

from datetime import datetime

from marshmallow import Schema, ValidationError, fields, validates

from app.models import MovementType, ProcessStage


class UserCreateSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    role = fields.Str(load_default="operator")
    is_active = fields.Bool(load_default=True)


class UserUpdateSchema(Schema):
    username = fields.Str()
    email = fields.Email()
    password = fields.Str(load_only=True)
    role = fields.Str()
    is_active = fields.Bool()


class DesignCreateSchema(Schema):
    design_code = fields.Str(required=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    metal_type = fields.Str(allow_none=True)
    target_weight_grams = fields.Float(allow_none=True)
    is_active = fields.Bool(load_default=True)


class DesignUpdateSchema(Schema):
    design_code = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    metal_type = fields.Str(allow_none=True)
    target_weight_grams = fields.Float(allow_none=True)
    is_active = fields.Bool()


class InventoryMovementCreateSchema(Schema):
    design_id = fields.Int(required=True)
    stage = fields.Str(required=True)
    movement_type = fields.Str(required=True)
    quantity = fields.Float(required=True)
    reference_no = fields.Str(allow_none=True)
    remarks = fields.Str(allow_none=True)
    movement_at = fields.DateTime(load_default=datetime.utcnow)
    performed_by_user_id = fields.Int(required=True)

    @validates("stage")
    def validate_stage(self, value: str, **kwargs) -> None:
        if value not in {item.value for item in ProcessStage}:
            raise ValidationError(f"Invalid stage. Allowed: {[item.value for item in ProcessStage]}")

    @validates("movement_type")
    def validate_movement_type(self, value: str, **kwargs) -> None:
        if value not in {item.value for item in MovementType}:
            raise ValidationError(
                f"Invalid movement_type. Allowed: {[item.value for item in MovementType]}"
            )

    @validates("quantity")
    def validate_quantity(self, value: float, **kwargs) -> None:
        if value <= 0:
            raise ValidationError("Quantity must be greater than zero")


class InventoryMovementUpdateSchema(InventoryMovementCreateSchema):
    design_id = fields.Int()
    stage = fields.Str()
    movement_type = fields.Str()
    quantity = fields.Float()
    performed_by_user_id = fields.Int()


class StageStockQuerySchema(Schema):
    design_id = fields.Int(required=False)
    stage = fields.Str(required=False)

    @validates("stage")
    def validate_stage(self, value: str, **kwargs) -> None:
        if value not in {item.value for item in ProcessStage}:
            raise ValidationError(f"Invalid stage. Allowed: {[item.value for item in ProcessStage]}")
