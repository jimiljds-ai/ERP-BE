from __future__ import annotations

from collections import defaultdict

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Design, InventoryMovement, MovementType, ProcessStage, User
from app.schemas import (
    DesignCreateSchema,
    DesignUpdateSchema,
    InventoryMovementCreateSchema,
    InventoryMovementUpdateSchema,
    StageStockQuerySchema,
    UserCreateSchema,
    UserUpdateSchema,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()
design_create_schema = DesignCreateSchema()
design_update_schema = DesignUpdateSchema()
movement_create_schema = InventoryMovementCreateSchema()
movement_update_schema = InventoryMovementUpdateSchema()
stage_stock_query_schema = StageStockQuerySchema()


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }


def design_to_dict(design: Design) -> dict:
    return {
        "id": design.id,
        "design_code": design.design_code,
        "name": design.name,
        "description": design.description,
        "metal_type": design.metal_type,
        "target_weight_grams": design.target_weight_grams,
        "is_active": design.is_active,
        "created_at": design.created_at.isoformat(),
        "updated_at": design.updated_at.isoformat(),
    }


def movement_to_dict(movement: InventoryMovement) -> dict:
    return {
        "id": movement.id,
        "design_id": movement.design_id,
        "stage": movement.stage.value,
        "movement_type": movement.movement_type.value,
        "quantity": movement.quantity,
        "signed_quantity": movement.signed_quantity,
        "reference_no": movement.reference_no,
        "remarks": movement.remarks,
        "movement_at": movement.movement_at.isoformat(),
        "performed_by_user_id": movement.performed_by_user_id,
        "created_at": movement.created_at.isoformat(),
        "updated_at": movement.updated_at.isoformat(),
    }


def parse_or_400(schema, payload):
    try:
        return schema.load(payload), None
    except ValidationError as err:
        return None, (jsonify({"errors": err.messages}), 400)


@api_bp.get("/health")
def health_check():
    return jsonify({"status": "ok"})


@api_bp.post("/users")
def create_user():
    payload, error = parse_or_400(user_create_schema, request.get_json() or {})
    if error:
        return error

    user = User(
        username=payload["username"],
        email=payload["email"],
        role=payload.get("role", "operator"),
        is_active=payload.get("is_active", True),
    )
    user.set_password(payload["password"])
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username or email already exists"}), 409

    return jsonify(user_to_dict(user)), 201


@api_bp.get("/users")
def list_users():
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([user_to_dict(user) for user in users])


@api_bp.get("/users/<int:user_id>")
def get_user(user_id: int):
    user = User.query.get_or_404(user_id)
    return jsonify(user_to_dict(user))


@api_bp.put("/users/<int:user_id>")
def update_user(user_id: int):
    user = User.query.get_or_404(user_id)
    payload, error = parse_or_400(user_update_schema, request.get_json() or {})
    if error:
        return error

    for field in ["username", "email", "role", "is_active"]:
        if field in payload:
            setattr(user, field, payload[field])

    if "password" in payload:
        user.set_password(payload["password"])

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username or email already exists"}), 409

    return jsonify(user_to_dict(user))


@api_bp.delete("/users/<int:user_id>")
def delete_user(user_id: int):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return "", 204


@api_bp.post("/designs")
def create_design():
    payload, error = parse_or_400(design_create_schema, request.get_json() or {})
    if error:
        return error

    design = Design(**payload)
    db.session.add(design)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "design_code already exists"}), 409

    return jsonify(design_to_dict(design)), 201


@api_bp.get("/designs")
def list_designs():
    designs = Design.query.order_by(Design.id.asc()).all()
    return jsonify([design_to_dict(design) for design in designs])


@api_bp.get("/designs/<int:design_id>")
def get_design(design_id: int):
    design = Design.query.get_or_404(design_id)
    return jsonify(design_to_dict(design))


@api_bp.put("/designs/<int:design_id>")
def update_design(design_id: int):
    design = Design.query.get_or_404(design_id)
    payload, error = parse_or_400(design_update_schema, request.get_json() or {})
    if error:
        return error

    for field, value in payload.items():
        setattr(design, field, value)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "design_code already exists"}), 409

    return jsonify(design_to_dict(design))


@api_bp.delete("/designs/<int:design_id>")
def delete_design(design_id: int):
    design = Design.query.get_or_404(design_id)
    db.session.delete(design)
    db.session.commit()
    return "", 204


@api_bp.post("/movements")
def create_movement():
    payload, error = parse_or_400(movement_create_schema, request.get_json() or {})
    if error:
        return error

    Design.query.get_or_404(payload["design_id"])
    User.query.get_or_404(payload["performed_by_user_id"])

    movement = InventoryMovement(
        design_id=payload["design_id"],
        stage=ProcessStage(payload["stage"]),
        movement_type=MovementType(payload["movement_type"]),
        quantity=payload["quantity"],
        reference_no=payload.get("reference_no"),
        remarks=payload.get("remarks"),
        movement_at=payload["movement_at"],
        performed_by_user_id=payload["performed_by_user_id"],
    )
    db.session.add(movement)
    db.session.commit()

    return jsonify(movement_to_dict(movement)), 201


@api_bp.get("/movements")
def list_movements():
    query = InventoryMovement.query.order_by(InventoryMovement.movement_at.desc())

    design_id = request.args.get("design_id", type=int)
    stage = request.args.get("stage")
    if design_id:
        query = query.filter(InventoryMovement.design_id == design_id)
    if stage:
        if stage not in {item.value for item in ProcessStage}:
            return jsonify({"error": "Invalid stage filter"}), 400
        query = query.filter(InventoryMovement.stage == ProcessStage(stage))

    movements = query.all()
    return jsonify([movement_to_dict(movement) for movement in movements])


@api_bp.get("/movements/<int:movement_id>")
def get_movement(movement_id: int):
    movement = InventoryMovement.query.get_or_404(movement_id)
    return jsonify(movement_to_dict(movement))


@api_bp.put("/movements/<int:movement_id>")
def update_movement(movement_id: int):
    movement = InventoryMovement.query.get_or_404(movement_id)
    payload, error = parse_or_400(movement_update_schema, request.get_json() or {})
    if error:
        return error

    if "design_id" in payload:
        Design.query.get_or_404(payload["design_id"])
        movement.design_id = payload["design_id"]
    if "performed_by_user_id" in payload:
        User.query.get_or_404(payload["performed_by_user_id"])
        movement.performed_by_user_id = payload["performed_by_user_id"]
    if "stage" in payload:
        movement.stage = ProcessStage(payload["stage"])
    if "movement_type" in payload:
        movement.movement_type = MovementType(payload["movement_type"])

    for field in ["quantity", "reference_no", "remarks", "movement_at"]:
        if field in payload:
            setattr(movement, field, payload[field])

    db.session.commit()
    return jsonify(movement_to_dict(movement))


@api_bp.delete("/movements/<int:movement_id>")
def delete_movement(movement_id: int):
    movement = InventoryMovement.query.get_or_404(movement_id)
    db.session.delete(movement)
    db.session.commit()
    return "", 204


@api_bp.get("/reports/stage-stock")
def stage_stock_report():
    query_params, error = parse_or_400(stage_stock_query_schema, request.args)
    if error:
        return error

    query = InventoryMovement.query
    if query_params.get("design_id"):
        query = query.filter(InventoryMovement.design_id == query_params["design_id"])
    if query_params.get("stage"):
        query = query.filter(InventoryMovement.stage == ProcessStage(query_params["stage"]))

    grouped_stock = defaultdict(float)
    for movement in query.all():
        grouped_stock[(movement.design_id, movement.stage.value)] += movement.signed_quantity

    rows = [
        {"design_id": design_id, "stage": stage, "current_stock": stock}
        for (design_id, stage), stock in sorted(grouped_stock.items())
    ]
    return jsonify(rows)
