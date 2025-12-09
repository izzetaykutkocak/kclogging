#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Blueprint

Main Flask blueprint for the immutable log widget.
"""

from flask import Blueprint
from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class WidgetConfig:
    """
    Configuration for the Immutable Log Widget.

    Attributes:
        log_file_path: Absolute path to the log file to display
        auth_decorator: Optional decorator function for authentication/authorization
        chunk_size: Number of lines to return per API request (default: 1000)
        enable_download: Whether to allow log file downloads (default: True)
        url_prefix: URL prefix for all widget routes (default: "/immutable_logs")
    """

    log_file_path: str
    auth_decorator: Optional[Callable] = None
    chunk_size: int = 1000
    enable_download: bool = True
    url_prefix: str = "/immutable_logs"

    def __post_init__(self):
        """Validate configuration after initialization."""
        import os

        if not self.log_file_path:
            raise ValueError("log_file_path is required")

        if not os.path.exists(self.log_file_path):
            raise FileNotFoundError(f"Log file not found: {self.log_file_path}")

        if not os.access(self.log_file_path, os.R_OK):
            raise PermissionError(f"Log file not readable: {self.log_file_path}")

        if not (100 <= self.chunk_size <= 10000):
            raise ValueError("chunk_size must be between 100 and 10000")


def create_blueprint(config: WidgetConfig) -> Blueprint:
    """
    Create and configure a Flask Blueprint for the log widget.

    Args:
        config: Widget configuration object

    Returns:
        Blueprint: Configured Flask Blueprint

    Example:
        config = WidgetConfig(log_file_path="/var/log/app.log")
        bp = create_blueprint(config)
        app.register_blueprint(bp)
    """
    bp = Blueprint(
        "immutable_logs",
        __name__,
        url_prefix=config.url_prefix,
        template_folder="../templates",
        static_folder="../static",
        static_url_path="/static",
    )

    # Store config in blueprint for access in routes
    bp.config = config

    # Import and register routes
    from . import routes

    routes.register_routes(bp, config)

    return bp
