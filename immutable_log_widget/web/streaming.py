#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streaming

Efficient log file streaming for large files without loading them into memory.
"""

import os
import re
import hashlib
from typing import Generator, Dict, Optional
from itertools import islice


class LogStreamer:
    """
    Efficiently stream log file contents using generators.

    Designed to handle multi-GB files without loading them into memory.
    Uses Python generators to yield lines one at a time.
    """

    HASH_PATTERN = re.compile(r"\[HASH:([a-f0-9]{64})\]")

    def __init__(self, log_file_path: str, chunk_size: int = 1000):
        """
        Initialize the log streamer.

        Args:
            log_file_path: Path to the log file
            chunk_size: Number of lines to process in each chunk
        """
        self.log_file_path = log_file_path
        self.chunk_size = chunk_size
        self._validate_file()

    def _validate_file(self):
        """Validate that the file exists and is readable."""
        if not os.path.exists(self.log_file_path):
            raise FileNotFoundError(f"Log file not found: {self.log_file_path}")

        if not os.path.isfile(self.log_file_path):
            raise ValueError(f"Path is not a file: {self.log_file_path}")

        if not os.access(self.log_file_path, os.R_OK):
            raise PermissionError(f"File is not readable: {self.log_file_path}")

    def stream_lines(
        self, start_line: int = 0, end_line: Optional[int] = None
    ) -> Generator[Dict, None, None]:
        """
        Stream log lines as a generator.

        Args:
            start_line: Starting line number (0-indexed)
            end_line: Ending line number (exclusive), None for end of file

        Yields:
            dict: {
                "line_number": int,    # 1-indexed line number
                "content": str,        # Full line content
                "hash": str,           # Extracted hash
                "content_no_hash": str # Content without hash prefix
            }
        """
        with open(self.log_file_path, "r", encoding="utf-8", buffering=8192) as f:
            if start_line > 0:
                for _ in islice(f, start_line):
                    pass

            line_iterator = enumerate(f, start=start_line + 1)

            if end_line is not None:
                line_iterator = islice(line_iterator, end_line - start_line)

            for line_num, line in line_iterator:
                line = line.rstrip("\n\r")

                hash_value = self.extract_hash(line)
                content_no_hash = self.remove_hash_prefix(line)

                yield {
                    "line_number": line_num,
                    "content": line,
                    "hash": hash_value if hash_value else "",
                    "content_no_hash": content_no_hash,
                }

    def get_total_lines(self) -> int:
        """
        Get total number of lines in the file efficiently.

        Uses buffered reading to count lines without loading entire file.

        Returns:
            int: Total number of lines
        """
        with open(self.log_file_path, "rb") as f:
            return sum(1 for _ in f)

    def get_file_size(self) -> int:
        """
        Get file size in bytes.

        Returns:
            int: File size in bytes
        """
        return os.path.getsize(self.log_file_path)

    def get_file_size_human(self) -> str:
        """
        Get human-readable file size.

        Returns:
            str: File size like "1.5 MB", "2.3 GB"
        """
        size = self.get_file_size()

        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0

        return f"{size:.1f} PB"

    def extract_hash(self, line: str) -> Optional[str]:
        """Extract hash from a log line."""
        match = self.HASH_PATTERN.search(line)
        if match:
            return match.group(1)
        return None

    def remove_hash_prefix(self, line: str) -> str:
        """Remove hash prefix from a log line."""
        match = self.HASH_PATTERN.search(line)
        if match:
            return line[match.end() :]
        return line


class ValidatingLogStreamer(LogStreamer):
    """
    Stream log lines with real-time integrity validation.

    Extends LogStreamer to validate each line's hash as it's streamed,
    allowing for efficient tamper detection without loading the entire file.
    """

    LOG_LEVEL_PATTERN = re.compile(r"\b(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)\b")
    GENESIS_HASH = hashlib.sha256(b"GENESIS").hexdigest()

    def __init__(self, log_file_path: str, chunk_size: int = 1000):
        """Initialize the validating streamer."""
        super().__init__(log_file_path, chunk_size)

    def stream_lines(
        self, start_line: int = 0, end_line: Optional[int] = None
    ) -> Generator[Dict, None, None]:
        """
        Stream log lines with validation.

        Args:
            start_line: Starting line number (0-indexed)
            end_line: Ending line number (exclusive)

        Yields:
            dict: {
                "line_number": int,      # 1-indexed line number
                "content": str,          # Full line content
                "hash": str,             # Extracted hash
                "is_valid": bool,        # True if hash is valid
                "log_level": str,        # Extracted log level (ERROR, WARN, INFO, DEBUG)
                "content_no_hash": str   # Content without hash prefix
            }
        """
        previous_hash = self.GENESIS_HASH

        if start_line > 0:
            with open(self.log_file_path, "r", encoding="utf-8", buffering=8192) as f:
                for i, line in enumerate(f):
                    if i >= start_line:
                        break
                    line = line.rstrip("\n\r")
                    hash_value = self.extract_hash(line)
                    if hash_value:
                        previous_hash = hash_value

        for line_data in super().stream_lines(start_line, end_line):
            current_hash = line_data["hash"]
            content_no_hash = line_data["content_no_hash"]

            is_valid = self.validate_line_hash(current_hash, content_no_hash, previous_hash)

            log_level = self.extract_log_level(line_data["content"])

            line_data["is_valid"] = is_valid
            line_data["log_level"] = log_level

            if current_hash:
                previous_hash = current_hash

            yield line_data

    def validate_line_hash(self, current_hash: str, content: str, previous_hash: str) -> bool:
        """
        Validate a line's hash against the previous hash.

        Args:
            current_hash: Hash extracted from current line
            content: Line content without hash
            previous_hash: Hash from previous line

        Returns:
            bool: True if valid, False if tampered
        """
        if not current_hash:
            return False

        expected_hash = self.calculate_expected_hash(content, previous_hash)
        return current_hash == expected_hash

    def extract_log_level(self, content: str) -> str:
        """
        Extract log level from line content.

        Args:
            content: Log line content

        Returns:
            str: Log level (ERROR, WARN, INFO, DEBUG) or "UNKNOWN"
        """
        match = self.LOG_LEVEL_PATTERN.search(content)
        if match:
            level = match.group(1)
            if level == "WARNING":
                return "WARN"
            return level
        return "UNKNOWN"

    def calculate_expected_hash(self, content: str, previous_hash: str) -> str:
        """
        Calculate what the hash should be for given content.

        Args:
            content: Line content without hash
            previous_hash: Hash from previous line

        Returns:
            str: Expected hash (64 character hex string)
        """
        data_to_hash = previous_hash + content
        return hashlib.sha256(data_to_hash.encode("utf-8")).hexdigest()
