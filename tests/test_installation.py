#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test package installation and imports.
"""

import pytest
import sys
import subprocess


class TestInstallation:
    """Test package installation."""

    def test_package_imports(self):
        """Test all public APIs can be imported."""
        # Main widget
        from immutable_log_widget import ImmutableLogWidget

        assert ImmutableLogWidget is not None

        # Configuration
        from immutable_log_widget import ImmutableLogWidgetConfig

        assert ImmutableLogWidgetConfig is not None

        # Core components
        from immutable_log_widget import ImmutableFileHandler

        assert ImmutableFileHandler is not None

        from immutable_log_widget import LogIntegrityChecker

        assert LogIntegrityChecker is not None

    def test_version_available(self):
        """Test version information is available."""
        from immutable_log_widget import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_security_utils_import(self):
        """Test security utilities can be imported."""
        from immutable_log_widget.utils.security import (
            require_auth,
            require_role,
            create_auth_decorator,
            flask_login_required,
            api_key_required,
        )

        assert require_auth is not None
        assert require_role is not None
        assert create_auth_decorator is not None
        assert flask_login_required is not None
        assert api_key_required is not None

    def test_package_metadata(self):
        """Test package metadata is correct."""
        import immutable_log_widget

        assert hasattr(immutable_log_widget, "__version__")
        assert hasattr(immutable_log_widget, "__author__")
        assert hasattr(immutable_log_widget, "__license__")

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_pip_install_editable(self):
        """Test package can be installed in editable mode."""
        result = subprocess.run(["pip", "install", "-e", "."], capture_output=True, text=True)

        # Should succeed or already be installed
        assert result.returncode == 0 or "already satisfied" in result.stdout.lower()
