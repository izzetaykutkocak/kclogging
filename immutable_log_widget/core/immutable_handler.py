#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Immutable File Handler

A logging handler that writes logs with cryptographic hash chains
to ensure immutability and detect tampering.
"""

import logging
import hashlib
import threading
import os


class ImmutableFileHandler(logging.Handler):
    """
    A logging handler that writes logs with cryptographic hash chains
    to ensure immutability and detect tampering.

    Each log line is prefixed with a hash that is computed from the previous
    hash and the current log content, creating an immutable chain where any
    tampering breaks the chain and can be detected.

    Format: [HASH:xxxxx] timestamp - level - message
    """

    def __init__(self, filename: str, mode: str = "a", encoding: str = "utf-8"):
        """
        Initialize the handler with file path and options.

        Args:
            filename: Path to the log file
            mode: File open mode (default: 'a' for append)
            encoding: File encoding (default: 'utf-8')
        """
        super().__init__()
        self.filename = os.path.abspath(filename)
        self.mode = mode
        self.encoding = encoding
        self.file_handle = None
        self._lock = threading.Lock()
        self.last_hash = hashlib.sha256(b"GENESIS").hexdigest()

        self._open_file()
        self._load_last_hash()

    def _open_file(self):
        """Open the log file for writing."""
        try:
            self.file_handle = open(self.filename, self.mode, encoding=self.encoding)
        except Exception as e:
            raise IOError(f"Failed to open log file {self.filename}: {e}")

    def _load_last_hash(self):
        """Load the last hash from the existing log file if it exists."""
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            try:
                with open(self.filename, "r", encoding=self.encoding) as f:
                    lines = f.readlines()
                    for line in reversed(lines):
                        line = line.strip()
                        if line and line.startswith("[HASH:"):
                            hash_end = line.find("]")
                            if hash_end > 0:
                                hash_value = line[6:hash_end]
                                if len(hash_value) == 64:
                                    self.last_hash = hash_value
                                    break
            except Exception:
                pass

    def emit(self, record: logging.LogRecord):
        """
        Write a log record with hash chain.

        Args:
            record: LogRecord to be written
        """
        with self._lock:
            try:
                msg = self.format(record)

                content = f" {msg}"

                data_to_hash = self.last_hash + content
                current_hash = hashlib.sha256(data_to_hash.encode(self.encoding)).hexdigest()

                log_line = f"[HASH:{current_hash}]{content}\n"

                if self.file_handle is None or self.file_handle.closed:
                    self._open_file()

                self.file_handle.write(log_line)
                self.file_handle.flush()

                self.last_hash = current_hash

            except Exception:
                self.handleError(record)

    def get_last_hash(self) -> str:
        """
        Return the current last hash in the chain.

        Returns:
            str: The last hash value (64 character hex string)
        """
        return self.last_hash

    def get_file_path(self) -> str:
        """
        Return the absolute path to the log file.

        Returns:
            str: Absolute path to the log file
        """
        return self.filename

    def close(self):
        """Close the file handler."""
        with self._lock:
            if self.file_handle and not self.file_handle.closed:
                self.file_handle.close()
        super().close()
