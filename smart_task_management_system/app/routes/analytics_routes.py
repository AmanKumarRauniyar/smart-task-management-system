from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from app.models.task_model import Task
from app.utils.analytics import compute_task_analytics

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/api/analytics", methods=["GET"])
@login_required
def get_analytics():
    user_tasks = (
        Task.query.filter_by(user_id=current_user.id)
        .order_by(Task.created_date.desc())
        .all()
    )
    task_payload = [task.to_dict() for task in user_tasks]
    analytics_data = compute_task_analytics(task_payload)

    return jsonify({"success": True, "analytics": analytics_data}), 200
