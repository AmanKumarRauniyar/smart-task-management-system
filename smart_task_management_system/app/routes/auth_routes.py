from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models.task_model import Task
from app.models.user_model import User
from app.utils.analytics import compute_task_analytics

auth_bp = Blueprint("auth", __name__)


def _normalize_email(raw_email: str) -> str:
    """Validate and normalize user-provided email."""
    return validate_email(raw_email, check_deliverability=False).normalized


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if len(username) < 3 or len(username) > 80:
            flash("Username must be between 3 and 80 characters.", "danger")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        try:
            normalized_email = _normalize_email(email)
        except EmailNotValidError:
            flash("Please provide a valid email address.", "danger")
            return render_template("register.html")

        existing_user = User.query.filter(
            (User.username == username) | (User.email == normalized_email)
        ).first()
        if existing_user:
            flash("Username or email is already registered.", "danger")
            return render_template("register.html")

        try:
            user = User(username=username, email=normalized_email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Registration failed due to a server issue. Please try again.", "danger")
            return render_template("register.html")

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username_or_email = request.form.get("username_or_email", "").strip()
        password = request.form.get("password", "")

        if not username_or_email or not password:
            flash("Username/email and password are required.", "danger")
            return render_template("login.html")

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if not user or not user.check_password(password):
            flash("Invalid credentials. Please try again.", "danger")
            return render_template("login.html")

        login_user(user, remember=True)
        flash("Welcome back!", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
@login_required
def dashboard():
    tasks = (
        Task.query.filter_by(user_id=current_user.id)
        .order_by(Task.created_date.desc())
        .all()
    )
    analytics = compute_task_analytics([task.to_dict() for task in tasks])
    return render_template("dashboard.html", analytics=analytics)
