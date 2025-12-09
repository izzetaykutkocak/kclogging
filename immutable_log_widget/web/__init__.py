"""
Web module for Flask integration.

This module contains Flask blueprints, routes, and streaming functionality
for the web-based log viewer.
"""

from .streaming import LogStreamer, ValidatingLogStreamer

__all__ = [
    "LogStreamer",
    "ValidatingLogStreamer",
]
