from flask import Flask, jsonify, redirect, request, url_for
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()


def create_app(config_class=Config):
    """Application factory used by Flask and tests."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, async_mode=app.config.get("SOCKETIO_ASYNC_MODE", "threading"))

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "message": "Authentication required."}), 401
        return redirect(url_for("auth.login"))

    # Import models before creating tables/migrations interactions.
    from app.models.user_model import User
    from app.models.task_model import Task

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints are registered now; endpoints are implemented module-by-module.
    from app.routes.auth_routes import auth_bp
    from app.routes.task_routes import task_bp
    from app.routes.analytics_routes import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(analytics_bp)

    # Register socket events.
    from app.sockets.socket_events import register_socket_events

    register_socket_events(socketio)

    with app.app_context():
        db.create_all()

    return app
