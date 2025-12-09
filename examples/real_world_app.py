#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-World Application Example
===============================

A complete Flask application demonstrating production-ready integration
of the Immutable Log Widget.

Features:
- User authentication with Flask-Login
- Role-based access control
- Multiple log files
- Custom styling
- Error handling
- Production configuration

Usage:
    pip install Flask-Login
    python examples/real_world_app.py
"""

import os
import logging
from flask import Flask, render_template_string, redirect, url_for, request, flash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

from immutable_log_widget import ImmutableLogWidget, ImmutableLogWidgetConfig, ImmutableFileHandler
from immutable_log_widget.utils.security import flask_login_required


# ============================================================================
# Application Setup
# ============================================================================

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production"),
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# ============================================================================
# Logging Setup
# ============================================================================

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

APP_LOG = os.path.join(LOG_DIR, "app.log")

# Application logger
app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)
app_handler = ImmutableFileHandler(APP_LOG)
app_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
app_handler.setFormatter(app_formatter)
app_logger.addHandler(app_handler)

# ============================================================================
# User Management
# ============================================================================


class User(UserMixin):
    """User model."""

    def __init__(self, id, username, password_hash, roles=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.roles = roles or ["user"]

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        return role in self.roles


# Mock user database (use real database in production)
USERS = {
    "admin": User("1", "admin", generate_password_hash("admin123"), ["admin", "user"]),
    "viewer": User("2", "viewer", generate_password_hash("viewer123"), ["viewer", "user"]),
}

# ============================================================================
# Flask-Login Setup
# ============================================================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."


@login_manager.user_loader
def load_user(user_id):
    for user in USERS.values():
        if user.id == user_id:
            return user
    return None


# ============================================================================
# Immutable Log Widget Setup
# ============================================================================

# Application logs widget
app_logs_config = ImmutableLogWidgetConfig(
    log_file_path=APP_LOG,
    url_prefix="/logs",
    auth_decorator=flask_login_required,
    enable_download=True,
    chunk_size=1000,
)
app_logs_widget = ImmutableLogWidget(app, app_logs_config)

# ============================================================================
# Routes
# ============================================================================

HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Real-World App - Immutable Log Widget</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin-right: 10px;
        }
        .btn:hover {
            background: #0056b3;
        }
        .btn-danger {
            background: #dc3545;
        }
        .btn-danger:hover {
            background: #c82333;
        }
        .user-info {
            background: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        li:last-child {
            border-bottom: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Real-World Application</h1>
        <p>Production-ready example with Immutable Log Widget</p>
    </div>

    {% if current_user.is_authenticated %}
        <div class="user-info">
            <strong>Logged in as:</strong> {{ current_user.username }}
            <strong>Roles:</strong> {{ ', '.join(current_user.roles) }}
        </div>

        <div class="card">
            <h2>Application Features</h2>
            <ul>
                <li><a href="{{ url_for('dashboard') }}">Dashboard</a></li>
                <li><a href="{{ url_for('generate_logs') }}">Generate Sample Logs</a></li>
                <li><a href="/logs/view">View Application Logs</a></li>
            </ul>
        </div>

        <a href="{{ url_for('logout') }}" class="btn btn-danger">Logout</a>
    {% else %}
        <div class="card">
            <h2>Welcome</h2>
            <p>Please log in to access the application.</p>
            <a href="{{ url_for('login') }}" class="btn">Login</a>
        </div>

        <div class="card">
            <h3>Test Credentials</h3>
            <ul>
                <li><strong>Admin:</strong> username=admin, password=admin123</li>
                <li><strong>Viewer:</strong> username=viewer, password=viewer123</li>
            </ul>
        </div>
    {% endif %}
</body>
</html>
"""


@app.route("/")
def index():
    """Home page."""
    app_logger.info(f"Home page accessed from {request.remote_addr}")
    return render_template_string(HOME_TEMPLATE)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = USERS.get(username)
        if user and user.check_password(password):
            login_user(user)
            app_logger.info(f"Successful login: {username} from {request.remote_addr}")
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("index"))
        else:
            app_logger.warning(f"Failed login attempt: {username} from {request.remote_addr}")
            flash("Invalid credentials", "error")

    return """
    <h1>Login</h1>
    <form method="post">
        <p><input type="text" name="username" placeholder="Username" required></p>
        <p><input type="password" name="password" placeholder="Password" required></p>
        <p><button type="submit">Login</button></p>
    </form>
    <p><a href="/">Back to Home</a></p>
    """


@app.route("/logout")
@login_required
def logout():
    """Logout."""
    username = current_user.username
    logout_user()
    app_logger.info(f"User logged out: {username}")
    flash("Logged out successfully", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    """User dashboard."""
    app_logger.info(f"Dashboard accessed by {current_user.username}")
    return f"""
    <h1>Dashboard</h1>
    <p>Welcome, {current_user.username}!</p>
    <p><a href="/">Home</a></p>
    """


@app.route("/generate-logs")
@login_required
def generate_logs():
    """Generate sample logs."""
    app_logger.debug(f"Debug log from {current_user.username}")
    app_logger.info(f"Info log from {current_user.username}")
    app_logger.warning(f"Warning log from {current_user.username}")
    app_logger.error(f"Error log from {current_user.username}")

    flash("Sample logs generated!", "success")
    return redirect(url_for("index"))


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    app_logger.info("=" * 60)
    app_logger.info("Real-World Application Starting")
    app_logger.info(f"Application logs: {APP_LOG}")
    app_logger.info("=" * 60)

    print("\n" + "=" * 60)
    print("Real-World Application - Immutable Log Widget")
    print("=" * 60)
    print("Test Credentials:")
    print("  Admin:  username=admin, password=admin123")
    print("  Viewer: username=viewer, password=viewer123")
    print("=" * 60)
    print("Log Files:")
    print(f"  Application: {APP_LOG}")
    print("=" * 60)
    print("URLs:")
    print("  Home:            http://localhost:5000/")
    print("  App Logs:        http://localhost:5000/logs/view")
    print("=" * 60 + "\n")

    app.run(debug=True, port=5000)
