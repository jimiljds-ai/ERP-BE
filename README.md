# ERP Backend (Jewelry Manufacturing)

Flask backend for tracking stock inflow/outflow across jewelry subprocesses:

- CAD
- CAM
- TREE_MAKING
- CASTING
- FILING
- POLISHING
- PLATING
- ASSEMBLING

## Tech Stack

- Flask
- Flask-SQLAlchemy
- Marshmallow (request payload validation)
- Flask-Migrate (database migrations)

## Domain Modeling (Analysis)

The backend uses these core entities:

1. **User** (multi-user support)
   - `username`, `email`, `password_hash`, `role`, `is_active`
   - Methods: `set_password`, `verify_password`
2. **Design**
   - `design_code`, `name`, `description`, `metal_type`, `target_weight_grams`, `is_active`
3. **InventoryMovement**
   - Tracks each inflow/outflow event per design and subprocess stage
   - `design_id`, `stage`, `movement_type`, `quantity`, `movement_at`, `performed_by_user_id`, `reference_no`, `remarks`
   - Computed method/property: `signed_quantity` for stock calculation

`ProcessStage` and `MovementType` are enums to enforce valid values.

## Project Structure

- `manage.py` - app entrypoint for Flask CLI and shell
- `config.py` - configuration class
- `app/extensions.py` - SQLAlchemy and Migrate instances
- `app/models.py` - ORM models and enums
- `app/schemas.py` - Marshmallow validation schemas
- `app/routes.py` - REST API routes (CRUD + stock report)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
export FLASK_APP=manage.py
flask run
```

## Database Migration

```bash
export FLASK_APP=manage.py
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```


## UI Templates

A starter server-rendered UI is available at `/` to help manually test Users, Designs, and Movements APIs.

## REST API Endpoints

### Health
- `GET /api/health`

### Users (Multi-user)
- `POST /api/users`
- `GET /api/users`
- `GET /api/users/<user_id>`
- `PUT /api/users/<user_id>`
- `DELETE /api/users/<user_id>`

### Designs
- `POST /api/designs`
- `GET /api/designs`
- `GET /api/designs/<design_id>`
- `PUT /api/designs/<design_id>`
- `DELETE /api/designs/<design_id>`

### Inventory Movements
- `POST /api/movements`
- `GET /api/movements?design_id=1&stage=CASTING`
- `GET /api/movements/<movement_id>`
- `PUT /api/movements/<movement_id>`
- `DELETE /api/movements/<movement_id>`

### Reports
- `GET /api/reports/stage-stock?design_id=1&stage=CASTING`
  - Returns current stock by `design_id + stage` using `inflow - outflow`

## Example Payloads

### Create user

```json
{
  "username": "supervisor1",
  "email": "supervisor1@example.com",
  "password": "StrongPass123",
  "role": "supervisor"
}
```

### Create design

```json
{
  "design_code": "RING-001",
  "name": "Floral Ring",
  "description": "18k gold floral ring",
  "metal_type": "Gold",
  "target_weight_grams": 7.25
}
```

### Create movement

```json
{
  "design_id": 1,
  "stage": "CASTING",
  "movement_type": "INFLOW",
  "quantity": 20,
  "performed_by_user_id": 1,
  "reference_no": "CAST-BATCH-1001",
  "remarks": "Batch received"
}
```
