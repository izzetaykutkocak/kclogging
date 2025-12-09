"""
Unit tests for core functionality.
"""

import pytest
import os
import tempfile
import logging
from immutable_log_widget.core.immutable_handler import ImmutableFileHandler
from immutable_log_widget.core.integrity_checker import LogIntegrityChecker
from immutable_log_widget.web.streaming import LogStreamer, ValidatingLogStreamer


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing."""
    fd, path = tempfile.mkstemp(suffix=".log")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def sample_log_file(temp_log_file):
    """Create a log file with sample entries."""
    logger = logging.getLogger("test")
    logger.setLevel(logging.INFO)
    handler = ImmutableFileHandler(temp_log_file)
    logger.addHandler(handler)

    logger.info("First log entry")
    logger.warning("Second log entry")
    logger.error("Third log entry")

    handler.close()
    logger.removeHandler(handler)

    return temp_log_file


class TestImmutableFileHandler:
    """Test ImmutableFileHandler functionality."""

    def test_handler_creation(self, temp_log_file):
        """Test handler can be created."""
        handler = ImmutableFileHandler(temp_log_file)
        assert handler.get_file_path() == temp_log_file
        assert handler.get_last_hash() is not None
        handler.close()

    def test_log_writing(self, temp_log_file):
        """Test logs are written with hashes."""
        logger = logging.getLogger("test_write")
        logger.setLevel(logging.INFO)
        handler = ImmutableFileHandler(temp_log_file)
        logger.addHandler(handler)

        logger.info("Test message")
        handler.close()

        with open(temp_log_file, "r") as f:
            content = f.read()
            assert "[HASH:" in content
            assert "Test message" in content

    def test_hash_chain(self, temp_log_file):
        """Test hash chain is maintained."""
        logger = logging.getLogger("test_chain")
        logger.setLevel(logging.INFO)
        handler = ImmutableFileHandler(temp_log_file)
        logger.addHandler(handler)

        logger.info("Message 1")
        hash1 = handler.get_last_hash()

        logger.info("Message 2")
        hash2 = handler.get_last_hash()

        assert hash1 != hash2
        handler.close()


class TestLogIntegrityChecker:
    """Test LogIntegrityChecker functionality."""

    def test_verify_valid_log(self, sample_log_file):
        """Test verification of valid log file."""
        checker = LogIntegrityChecker(sample_log_file)
        result = checker.verify_full_log()

        assert result["valid"] is True
        assert result["total_lines"] == 3
        assert len(result["tampered_lines"]) == 0

    def test_verify_tampered_log(self, sample_log_file):
        """Test detection of tampered log."""
        with open(sample_log_file, "r") as f:
            lines = f.readlines()

        if len(lines) > 1:
            parts = lines[1].split("]", 1)
            if len(parts) == 2:
                lines[1] = parts[0] + "] TAMPERED CONTENT\n"

        with open(sample_log_file, "w") as f:
            f.writelines(lines)

        checker = LogIntegrityChecker(sample_log_file)
        result = checker.verify_full_log()

        assert result["valid"] is False
        assert len(result["tampered_lines"]) > 0

    def test_empty_file(self, temp_log_file):
        """Test verification of empty file."""
        checker = LogIntegrityChecker(temp_log_file)
        result = checker.verify_full_log()

        assert result["valid"] is True
        assert result["total_lines"] == 0


class TestLogStreamer:
    """Test LogStreamer functionality."""

    def test_stream_all_lines(self, sample_log_file):
        """Test streaming all lines."""
        streamer = LogStreamer(sample_log_file)
        lines = list(streamer.stream_lines())

        assert len(lines) == 3
        assert all("line_number" in line for line in lines)
        assert all("content" in line for line in lines)

    def test_stream_range(self, sample_log_file):
        """Test streaming a range of lines."""
        streamer = LogStreamer(sample_log_file)
        lines = list(streamer.stream_lines(start_line=1, end_line=2))

        assert len(lines) == 1
        assert lines[0]["line_number"] == 2

    def test_get_total_lines(self, sample_log_file):
        """Test line counting."""
        streamer = LogStreamer(sample_log_file)
        assert streamer.get_total_lines() == 3

    def test_get_file_size(self, sample_log_file):
        """Test file size retrieval."""
        streamer = LogStreamer(sample_log_file)
        size = streamer.get_file_size()
        assert size > 0


class TestValidatingLogStreamer:
    """Test ValidatingLogStreamer functionality."""

    def test_stream_with_validation(self, sample_log_file):
        """Test streaming with validation."""
        streamer = ValidatingLogStreamer(sample_log_file)
        lines = list(streamer.stream_lines())

        assert len(lines) == 3
        assert all("is_valid" in line for line in lines)
        assert all(line["is_valid"] for line in lines)

    def test_log_level_extraction(self, sample_log_file):
        """Test log level extraction."""
        streamer = ValidatingLogStreamer(sample_log_file)
        lines = list(streamer.stream_lines())

        assert len(lines) == 3
        assert all("log_level" in line for line in lines)
