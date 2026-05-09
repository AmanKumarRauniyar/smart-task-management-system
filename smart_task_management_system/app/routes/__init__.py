from app.routes.analytics_routes import analytics_bp
from app.routes.auth_routes import auth_bp
from app.routes.task_routes import task_bp

__all__ = ["auth_bp", "task_bp", "analytics_bp"]
