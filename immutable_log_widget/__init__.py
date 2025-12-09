#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Immutable Log Widget
====================

A Flask widget for viewing immutable log files with integrity validation.

Quick Start:
    from flask import Flask
    from immutable_log_widget import ImmutableLogWidget, ImmutableLogWidgetConfig

    app = Flask(__name__)
    config = ImmutableLogWidgetConfig(log_file_path="/path/to/logs/app.log")
    widget = ImmutableLogWidget(app, config)

    app.run()
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

from .core.immutable_handler import ImmutableFileHandler
from .core.integrity_checker import LogIntegrityChecker
from .utils.config import ImmutableLogWidgetConfig
from .web.blueprint import create_blueprint, WidgetConfig

from flask import Flask
from typing import Optional


class ImmutableLogWidget:
    """
    Main widget class for integrating immutable log viewing into Flask apps.

    Supports both direct initialization and Flask application factory pattern.

    Examples:
        # Direct initialization
        app = Flask(__name__)
        config = ImmutableLogWidgetConfig(log_file_path="/var/log/app.log")
        widget = ImmutableLogWidget(app, config)

        # Factory pattern
        widget = ImmutableLogWidget()

        def create_app():
            app = Flask(__name__)
            config = ImmutableLogWidgetConfig(log_file_path="/var/log/app.log")
            widget.init_app(app, config)
            return app
    """

    def __init__(
        self, app: Optional[Flask] = None, config: Optional[ImmutableLogWidgetConfig] = None
    ):
        """
        Initialize the widget.

        Args:
            app: Flask application instance (optional for factory pattern)
            config: Widget configuration (optional for factory pattern)
        """
        self.app = app
        self.config = config
        self.blueprint = None

        if app is not None and config is not None:
            self.init_app(app, config)

    def init_app(self, app: Flask, config: ImmutableLogWidgetConfig):
        """
        Initialize the widget with a Flask application.

        This method can be called multiple times with different apps
        (useful for testing or multi-app scenarios).

        Args:
            app: Flask application instance
            config: Widget configuration

        Raises:
            ValueError: If app is not a Flask instance
            TypeError: If config is not ImmutableLogWidgetConfig
        """
        if not isinstance(app, Flask):
            raise ValueError("app must be a Flask instance")

        if not isinstance(config, ImmutableLogWidgetConfig):
            raise TypeError("config must be an ImmutableLogWidgetConfig instance")

        self.app = app
        self.config = config

        self.blueprint = self._create_blueprint()
        app.register_blueprint(self.blueprint)

        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["immutable_log_widget"] = self

        app.logger.info(
            f"Immutable Log Widget initialized: "
            f"file={config.log_file_path}, "
            f"url_prefix={config.url_prefix}"
        )

    def _create_blueprint(self):
        """
        Create the Flask Blueprint with current configuration.

        Returns:
            Blueprint: Configured Flask Blueprint
        """
        widget_config = WidgetConfig(
            log_file_path=self.config.log_file_path,
            auth_decorator=self.config.auth_decorator,
            chunk_size=self.config.chunk_size,
            enable_download=self.config.enable_download,
            url_prefix=self.config.url_prefix,
        )

        return create_blueprint(widget_config)

    def get_log_handler(self) -> ImmutableFileHandler:
        """
        Get a configured ImmutableFileHandler for logging.

        This allows you to use the same log file that the widget displays.

        Returns:
            ImmutableFileHandler: Configured handler

        Example:
            import logging

            logger = logging.getLogger('myapp')
            handler = widget.get_log_handler()
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        """
        return ImmutableFileHandler(self.config.log_file_path)

    def verify_integrity(self) -> dict:
        """
        Programmatically verify log file integrity.

        Returns:
            dict: Verification results with keys:
                - valid (bool): True if all lines are valid
                - total_lines (int): Total number of lines
                - tampered_lines (list): List of tampered line numbers

        Example:
            result = widget.verify_integrity()
            if result['valid']:
                print("Log is valid!")
            else:
                print(f"Found {len(result['tampered_lines'])} tampered lines")
        """
        checker = LogIntegrityChecker(self.config.log_file_path)
        return checker.verify_full_log()

    def get_viewer_url(self) -> str:
        """
        Get the URL for the log viewer page.

        Returns:
            str: Relative URL to the viewer page

        Example:
            print(f"View logs at: {widget.get_viewer_url()}")
        """
        return f"{self.config.url_prefix}/view"

    def get_api_urls(self) -> dict:
        """
        Get all API endpoint URLs.

        Returns:
            dict: Dictionary of endpoint names to URLs

        Example:
            urls = widget.get_api_urls()
            print(f"Stream API: {urls['stream']}")
        """
        prefix = self.config.url_prefix
        return {
            "view": f"{prefix}/view",
            "stream": f"{prefix}/api/stream",
            "download": f"{prefix}/api/download",
            "verify": f"{prefix}/api/verify",
        }

    @property
    def is_initialized(self) -> bool:
        """Check if widget is initialized with an app."""
        return self.app is not None and self.blueprint is not None

    def __repr__(self) -> str:
        """String representation of the widget."""
        status = "initialized" if self.is_initialized else "not initialized"
        return f"<ImmutableLogWidget {status}>"


__all__ = [
    "ImmutableLogWidget",
    "ImmutableLogWidgetConfig",
    "ImmutableFileHandler",
    "LogIntegrityChecker",
    "__version__",
]
