#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic Integration Example
=========================

Demonstrates the simplest possible integration of the Immutable Log Widget.

This example shows:
- Minimal configuration
- No authentication
- Default settings

Usage:
    python examples/basic_integration.py

Then visit: http://localhost:5000/immutable_logs/view
"""

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from immutable_log_widget import ImmutableLogWidget, ImmutableLogWidgetConfig, ImmutableFileHandler


app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"

LOG_FILE = os.path.join(os.path.dirname(__file__), "app.log")

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

handler = ImmutableFileHandler(LOG_FILE)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

config = ImmutableLogWidgetConfig(log_file_path=LOG_FILE, enable_download=True, chunk_size=1000)

widget = ImmutableLogWidget(app, config)


@app.route("/")
def index():
    logger.info("Index page accessed")
    return f"""
    <h1>Immutable Log Widget - Basic Example</h1>
    <p>This is a basic Flask app with immutable logging.</p>
    <ul>
        <li><a href="/generate-logs">Generate Sample Logs</a></li>
        <li><a href="{widget.get_viewer_url()}">View Logs</a></li>
    </ul>
    """


@app.route("/generate-logs")
def generate_logs():
    """Generate sample log entries."""
    logger.debug("Debug message - detailed information")
    logger.info("Info message - general information")
    logger.warning("Warning message - something to watch")
    logger.error("Error message - something went wrong")

    return """
    <h2>Logs Generated!</h2>
    <p>Sample logs have been written to the log file.</p>
    <p><a href="/">Back to Home</a> | <a href="/immutable_logs/view">View Logs</a></p>
    """


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Application starting")
    logger.info(f"Log file: {LOG_FILE}")
    logger.info(f"Log viewer URL: {widget.get_viewer_url()}")
    logger.info("=" * 50)

    print("\n" + "=" * 60)
    print("Immutable Log Widget - Basic Example")
    print("=" * 60)
    print(f"Log file: {LOG_FILE}")
    print(f"Log viewer: http://localhost:5000{widget.get_viewer_url()}")
    print("=" * 60 + "\n")

    app.run(debug=True, port=5000)
