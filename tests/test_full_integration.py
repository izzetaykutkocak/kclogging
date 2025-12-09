#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full integration tests with complete Flask application.
"""

import pytest
import os
import tempfile
import logging
from flask import Flask
from flask_login import LoginManager, UserMixin, login_user
from immutable_log_widget import ImmutableLogWidget, ImmutableLogWidgetConfig, ImmutableFileHandler
from immutable_log_widget.utils.security import flask_login_required


class User(UserMixin):
    """Test user model."""

    def __init__(self, id, username):
        self.id = id
        self.username = username


@pytest.fixture
def full_app():
    """Create a complete Flask application with authentication."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-secret-key"

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id, f"user{user_id}")

    # Create log file
    fd, log_path = tempfile.mkstemp(suffix=".log")
    os.close(fd)

    # Setup logging
    logger = logging.getLogger("full_test")
    logger.setLevel(logging.INFO)
    handler = ImmutableFileHandler(log_path)
    logger.addHandler(handler)

    # Generate test logs
    for i in range(100):
        logger.info(f"Test log entry {i + 1}")

    handler.close()

    # Configure widget with authentication
    config = ImmutableLogWidgetConfig(
        log_file_path=log_path, auth_decorator=flask_login_required, enable_download=True
    )

    widget = ImmutableLogWidget(app, config)

    # Add test routes
    @app.route("/login/<user_id>")
    def login(user_id):
        user = User(user_id, f"user{user_id}")
        login_user(user)
        return "Logged in"

    yield app, widget, log_path

    # Cleanup
    if os.path.exists(log_path):
        os.unlink(log_path)


class TestFullIntegration:
    """Test complete application integration."""

    def test_widget_initialization(self, full_app):
        """Test widget is properly initialized."""
        app, widget, _ = full_app

        assert widget.is_initialized
        assert "immutable_log_widget" in app.extensions
        assert app.extensions["immutable_log_widget"] is widget

    def test_unauthenticated_access_denied(self, full_app):
        """Test unauthenticated users cannot access logs."""
        app, widget, _ = full_app
        client = app.test_client()

        response = client.get("/immutable_logs/view")
        assert response.status_code == 401

    def test_authenticated_access_allowed(self, full_app):
        """Test authenticated users can access logs."""
        app, widget, _ = full_app
        client = app.test_client()

        # Login first
        client.get("/login/1")

        # Access logs
        response = client.get("/immutable_logs/view")
        assert response.status_code == 200
        assert b"Immutable Log Viewer" in response.data

    def test_full_workflow(self, full_app):
        """Test complete user workflow."""
        app, widget, _ = full_app
        client = app.test_client()

        # 1. Login
        response = client.get("/login/1")
        assert response.status_code == 200

        # 2. View logs
        response = client.get("/immutable_logs/view")
        assert response.status_code == 200

        # 3. Stream logs
        response = client.get("/immutable_logs/api/stream?start=0&count=10")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["lines"]) == 10

        # 4. Verify integrity
        response = client.post("/immutable_logs/api/verify")
        assert response.status_code == 200
        data = response.get_json()
        assert data["valid"] is True

        # 5. Download logs
        response = client.get("/immutable_logs/api/download")
        assert response.status_code == 200

    def test_programmatic_verification(self, full_app):
        """Test programmatic integrity verification."""
        app, widget, _ = full_app

        result = widget.verify_integrity()
        assert result["valid"] is True
        assert result["total_lines"] == 100
        assert len(result["tampered_lines"]) == 0

    def test_url_helpers(self, full_app):
        """Test URL helper methods."""
        app, widget, _ = full_app

        viewer_url = widget.get_viewer_url()
        assert viewer_url == "/immutable_logs/view"

        api_urls = widget.get_api_urls()
        assert "view" in api_urls
        assert "stream" in api_urls
        assert "download" in api_urls
        assert "verify" in api_urls
