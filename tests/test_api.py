"""
Integration tests for API endpoints.
"""

import pytest
import os
import tempfile
import logging
from flask import Flask
from immutable_log_widget import ImmutableLogWidget, ImmutableLogWidgetConfig, ImmutableFileHandler


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-secret-key"
    return app


@pytest.fixture
def test_log_file():
    """Create test log file."""
    fd, path = tempfile.mkstemp(suffix=".log")
    os.close(fd)

    logger = logging.getLogger("test_api")
    logger.setLevel(logging.INFO)
    handler = ImmutableFileHandler(path)
    logger.addHandler(handler)

    for i in range(10):
        logger.info(f"Test log entry {i + 1}")

    handler.close()
    logger.removeHandler(handler)

    yield path

    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def widget(app, test_log_file):
    """Create widget instance."""
    config = ImmutableLogWidgetConfig(log_file_path=test_log_file, enable_download=True)
    widget = ImmutableLogWidget(app, config)
    return widget


@pytest.fixture
def client(app, widget):
    """Create test client."""
    return app.test_client()


class TestViewEndpoint:
    """Test the view endpoint."""

    def test_view_returns_html(self, client):
        """Test view endpoint returns HTML."""
        response = client.get("/immutable_logs/view")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data
        assert b"Immutable Log Viewer" in response.data

    def test_view_contains_config(self, client):
        """Test view contains configuration."""
        response = client.get("/immutable_logs/view")
        assert b"LOG_VIEWER_CONFIG" in response.data


class TestStreamEndpoint:
    """Test the stream API endpoint."""

    def test_stream_returns_json(self, client):
        """Test stream endpoint returns JSON."""
        response = client.get("/immutable_logs/api/stream")
        assert response.status_code == 200
        assert response.content_type == "application/json"

    def test_stream_returns_lines(self, client):
        """Test stream returns log lines."""
        response = client.get("/immutable_logs/api/stream?start=0&count=5")
        data = response.get_json()

        assert "lines" in data
        assert "has_more" in data
        assert "total_lines" in data
        assert len(data["lines"]) <= 5

    def test_stream_pagination(self, client):
        """Test stream pagination."""
        response = client.get("/immutable_logs/api/stream?start=5&count=5")
        data = response.get_json()

        assert data["start"] == 5
        assert len(data["lines"]) <= 5

    def test_stream_invalid_params(self, client):
        """Test stream with invalid parameters."""
        response = client.get("/immutable_logs/api/stream?start=-1")
        assert response.status_code == 400


class TestDownloadEndpoint:
    """Test the download endpoint."""

    def test_download_returns_file(self, client):
        """Test download endpoint returns file."""
        response = client.get("/immutable_logs/api/download")
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "")

    def test_download_disabled(self, app, test_log_file):
        """Test download when disabled."""
        config = ImmutableLogWidgetConfig(log_file_path=test_log_file, enable_download=False)
        ImmutableLogWidget(app, config)
        client = app.test_client()

        response = client.get("/immutable_logs/api/download")
        assert response.status_code == 403


class TestVerifyEndpoint:
    """Test the verify endpoint."""

    def test_verify_returns_result(self, client):
        """Test verify endpoint returns result."""
        response = client.post("/immutable_logs/api/verify")
        assert response.status_code == 200

        data = response.get_json()
        assert "valid" in data
        assert "total_lines" in data
        assert "tampered_lines" in data

    def test_verify_valid_log(self, client):
        """Test verification of valid log."""
        response = client.post("/immutable_logs/api/verify")
        data = response.get_json()

        assert data["valid"] is True
        assert len(data["tampered_lines"]) == 0
