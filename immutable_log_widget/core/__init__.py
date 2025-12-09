"""
Core module for immutable logging functionality.

This module contains the core components for immutable log handling
and integrity verification.
"""

from .immutable_handler import ImmutableFileHandler
from .integrity_checker import LogIntegrityChecker

__all__ = [
    "ImmutableFileHandler",
    "LogIntegrityChecker",
]
