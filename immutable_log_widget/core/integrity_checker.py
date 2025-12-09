#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Integrity Checker

Module for verifying the integrity of immutable log files
by validating cryptographic hash chains.
"""

import hashlib
import re
import os
from typing import Dict, Optional


class LogIntegrityChecker:
    """
    Validates the integrity of immutable log files by verifying hash chains.

    Each log line contains a hash that is computed from the previous hash
    and the current line content. This creates a chain where any tampering
    breaks the chain and can be detected.
    """

    HASH_PATTERN = re.compile(r"\[HASH:([a-f0-9]{64})\]")
    GENESIS_HASH = hashlib.sha256(b"GENESIS").hexdigest()

    def __init__(self, log_file_path: str):
        """
        Initialize the integrity checker.

        Args:
            log_file_path: Path to the log file to verify
        """
        self.log_file_path = log_file_path

    def verify_full_log(self) -> Dict:
        """
        Verify the entire log file and return detailed results.

        Returns:
            dict: {
                "valid": bool,           # True if all lines are valid
                "total_lines": int,      # Total number of lines checked
                "tampered_lines": list,  # List of line numbers that are tampered
                "error": str or None     # Error message if file can't be read
            }
        """
        result = {"valid": True, "total_lines": 0, "tampered_lines": [], "error": None}

        if not os.path.exists(self.log_file_path):
            result["error"] = f"File not found: {self.log_file_path}"
            result["valid"] = False
            return result

        try:
            with open(self.log_file_path, "r", encoding="utf-8") as f:
                previous_hash = self.GENESIS_HASH
                line_number = 0

                for line in f:
                    line_number += 1
                    line = line.rstrip("\n\r")

                    if not line:
                        continue

                    if not self.verify_line(line_number, line, previous_hash):
                        result["tampered_lines"].append(line_number)
                        result["valid"] = False

                    extracted_hash = self.extract_hash_from_line(line)
                    if extracted_hash:
                        previous_hash = extracted_hash

                result["total_lines"] = line_number

        except PermissionError:
            result["error"] = f"Permission denied: {self.log_file_path}"
            result["valid"] = False
        except Exception as e:
            result["error"] = f"Error reading file: {str(e)}"
            result["valid"] = False

        return result

    def verify_line(self, line_number: int, line_content: str, previous_hash: str) -> bool:
        """
        Verify a single log line against the previous hash.

        Args:
            line_number: Line number (for error reporting)
            line_content: Full content of the log line
            previous_hash: Hash from the previous line

        Returns:
            bool: True if line is valid, False if tampered
        """
        extracted_hash = self.extract_hash_from_line(line_content)
        if not extracted_hash:
            return False

        content_without_hash = self.extract_content_without_hash(line_content)

        expected_hash = self.get_line_hash(content_without_hash, previous_hash)

        return extracted_hash == expected_hash

    def get_line_hash(self, line_content: str, previous_hash: str) -> str:
        """
        Calculate what the hash should be for a given line.

        Args:
            line_content: Content of the line (without the hash prefix)
            previous_hash: Hash from the previous line

        Returns:
            str: Calculated hash (64 character hex string)
        """
        data_to_hash = previous_hash + line_content
        return hashlib.sha256(data_to_hash.encode("utf-8")).hexdigest()

    def extract_hash_from_line(self, line: str) -> Optional[str]:
        """
        Extract the hash from a log line.

        Args:
            line: Full log line including hash

        Returns:
            str or None: Extracted hash or None if not found
        """
        match = self.HASH_PATTERN.search(line)
        if match:
            return match.group(1)
        return None

    def extract_content_without_hash(self, line: str) -> str:
        """
        Remove the hash prefix from a log line.

        Args:
            line: Full log line including hash

        Returns:
            str: Line content without the hash prefix
        """
        match = self.HASH_PATTERN.search(line)
        if match:
            return line[match.end() :]
        return line
