#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration management for the Immutable Log Widget.
"""

import os
from dataclasses import dataclass
from typing import Optional, Callable, List


@dataclass
class ImmutableLogWidgetConfig:
    """
    Configuration for the Immutable Log Widget.

    Attributes:
        log_file_path: Absolute path to the log file (required)
        url_prefix: URL prefix for all widget routes (default: "/immutable_logs")
        auth_decorator: Optional authentication decorator function
        require_roles: Optional list of required roles for access
        chunk_size: Number of lines per API request (default: 1000, range: 100-10000)
        enable_download: Allow log file downloads (default: True)
        max_file_size_mb: Maximum file size in MB (None = no limit)
        enable_verification: Allow integrity verification (default: True)
        auto_verify_on_load: Automatically verify integrity on page load (default: False)
    """

    log_file_path: str

    url_prefix: str = "/immutable_logs"

    auth_decorator: Optional[Callable] = None
    require_roles: Optional[List[str]] = None

    chunk_size: int = 1000
    max_file_size_mb: Optional[int] = None

    enable_download: bool = True
    enable_verification: bool = True
    auto_verify_on_load: bool = False

    custom_css: Optional[str] = None
    custom_js: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_log_file()
        self._validate_chunk_size()
        self._validate_file_size()
        self._validate_url_prefix()

    def _validate_log_file(self):
        """Validate log file path."""
        if not self.log_file_path:
            raise ValueError("log_file_path is required")

        if not os.path.isabs(self.log_file_path):
            raise ValueError(f"log_file_path must be absolute: {self.log_file_path}")

        if not os.path.exists(self.log_file_path):
            raise FileNotFoundError(f"Log file not found: {self.log_file_path}")

        if not os.path.isfile(self.log_file_path):
            raise ValueError(f"log_file_path must be a file: {self.log_file_path}")

        if not os.access(self.log_file_path, os.R_OK):
            raise PermissionError(f"Log file not readable: {self.log_file_path}")

    def _validate_chunk_size(self):
        """Validate chunk size."""
        if not isinstance(self.chunk_size, int):
            raise TypeError("chunk_size must be an integer")

        if not (100 <= self.chunk_size <= 10000):
            raise ValueError("chunk_size must be between 100 and 10000")

    def _validate_file_size(self):
        """Validate file size limits."""
        if self.max_file_size_mb is not None:
            if not isinstance(self.max_file_size_mb, (int, float)):
                raise TypeError("max_file_size_mb must be a number")

            if self.max_file_size_mb <= 0:
                raise ValueError("max_file_size_mb must be positive")

            file_size_mb = os.path.getsize(self.log_file_path) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                raise ValueError(
                    f"Log file size ({file_size_mb:.2f} MB) exceeds "
                    f"maximum allowed size ({self.max_file_size_mb} MB)"
                )

    def _validate_url_prefix(self):
        """Validate URL prefix."""
        if not self.url_prefix.startswith("/"):
            raise ValueError("url_prefix must start with '/'")

        if self.url_prefix.endswith("/"):
            self.url_prefix = self.url_prefix.rstrip("/")

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.

        Returns:
            dict: Configuration as dictionary
        """
        return {
            "log_file_path": self.log_file_path,
            "url_prefix": self.url_prefix,
            "chunk_size": self.chunk_size,
            "enable_download": self.enable_download,
            "enable_verification": self.enable_verification,
            "auto_verify_on_load": self.auto_verify_on_load,
            "max_file_size_mb": self.max_file_size_mb,
            "has_auth": self.auth_decorator is not None,
            "require_roles": self.require_roles,
        }

    @classmethod
    def from_dict(cls, config_dict: dict) -> "ImmutableLogWidgetConfig":
        """
        Create configuration from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            ImmutableLogWidgetConfig: Configuration instance
        """
        return cls(**config_dict)

    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"ImmutableLogWidgetConfig("
            f"log_file_path='{self.log_file_path}', "
            f"url_prefix='{self.url_prefix}', "
            f"auth={'enabled' if self.auth_decorator else 'disabled'}, "
            f"chunk_size={self.chunk_size})"
        )
