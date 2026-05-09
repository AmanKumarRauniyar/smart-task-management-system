from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app import db, socketio
from app.models.task_model import Task
from app.sockets.socket_events import user_room

task_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")

ALLOWED_PRIORITIES = {"Low", "Medium", "High"}
ALLOWED_STATUS = {"Pending", "In Progress", "Completed"}


def _error_response(message: str, status_code: int):
    return jsonify({"success": False, "message": message}), status_code


def _validate_task_payload(payload: dict, is_update: bool = False):
    if not payload:
        return "Request body must be valid JSON."
    if not isinstance(payload, dict):
        return "Request body must be a JSON object."

    if not is_update:
        required_fields = ["title", "description", "priority", "status"]
        for field in required_fields:
            if field not in payload:
                return f"Missing required field: {field}."

    if "title" in payload:
        title = str(payload.get("title", "")).strip()
        if not title:
            return "Title is required."
        if len(title) > 200:
            return "Title cannot exceed 200 characters."

    if "description" in payload:
        description = str(payload.get("description", "")).strip()
        if not description:
            return "Description is required."

    if "priority" in payload:
        if payload.get("priority") not in ALLOWED_PRIORITIES:
            return f"Priority must be one of: {', '.join(sorted(ALLOWED_PRIORITIES))}."

    if "status" in payload:
        if payload.get("status") not in ALLOWED_STATUS:
            return f"Status must be one of: {', '.join(sorted(ALLOWED_STATUS))}."

    return None


def _emit_task_event(action: str, user_id: int, task_payload: dict):
    """Emit user-scoped task events for real-time dashboard updates."""
    socketio.emit(
        "task_event",
        {
            "action": action,
            "message": f"Task '{task_payload['title']}' was {action}.",
            "task": task_payload,
        },
        room=user_room(user_id),
    )


@task_bp.route("", methods=["GET"])
@login_required
def get_tasks():
    tasks = (
        Task.query.filter_by(user_id=current_user.id)
        .order_by(Task.created_date.desc())
        .all()
    )
    return jsonify({"success": True, "tasks": [task.to_dict() for task in tasks]}), 200


@task_bp.route("", methods=["POST"])
@login_required
def create_task():
    payload = request.get_json(silent=True)
    validation_error = _validate_task_payload(payload)
    if validation_error:
        return _error_response(validation_error, 400)

    try:
        new_task = Task(
            title=payload["title"].strip(),
            description=payload["description"].strip(),
            priority=payload["priority"],
            status=payload["status"],
            user_id=current_user.id,
        )
        db.session.add(new_task)
        db.session.commit()
        _emit_task_event("created", current_user.id, new_task.to_dict())
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Task created successfully.",
                    "task": new_task.to_dict(),
                }
            ),
            201,
        )
    except Exception:
        db.session.rollback()
        return _error_response("Unable to create task due to a server error.", 500)


@task_bp.route("/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id: int):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return _error_response("Task not found.", 404)

    payload = request.get_json(silent=True)
    validation_error = _validate_task_payload(payload, is_update=True)
    if validation_error:
        return _error_response(validation_error, 400)

    if "title" in payload:
        task.title = payload["title"].strip()
    if "description" in payload:
        task.description = payload["description"].strip()
    if "priority" in payload:
        task.priority = payload["priority"]
    if "status" in payload:
        task.status = payload["status"]

    try:
        db.session.commit()
        _emit_task_event("updated", current_user.id, task.to_dict())
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Task updated successfully.",
                    "task": task.to_dict(),
                }
            ),
            200,
        )
    except Exception:
        db.session.rollback()
        return _error_response("Unable to update task due to a server error.", 500)


@task_bp.route("/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id: int):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return _error_response("Task not found.", 404)

    try:
        deleted_task_payload = task.to_dict()
        db.session.delete(task)
        db.session.commit()
        _emit_task_event("deleted", current_user.id, deleted_task_payload)
        return jsonify({"success": True, "message": "Task deleted successfully."}), 200
    except Exception:
        db.session.rollback()
        return _error_response("Unable to delete task due to a server error.", 500)
