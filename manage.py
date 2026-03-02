from app import create_app
from app.extensions import db
from app.models import Design, InventoryMovement, User

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Design": Design,
        "InventoryMovement": InventoryMovement,
    }
