
from backend.routes.auth import auth_bp
from backend.routes.customer import cust_bp
from backend.routes.ticket import ticket_bp
from backend.routes.dashboard import dash_bp

__all__ = [
    "auth_bp",
    "cust_bp",
    "ticket_bp",
    "dash_bp",
]
