"""
Performance tests for large file handling.
"""

import pytest
import os
import tempfile
import logging
import time
from immutable_log_widget.core.immutable_handler import ImmutableFileHandler
from immutable_log_widget.web.streaming import ValidatingLogStreamer


@pytest.fixture
def large_log_file():
    """Create a large log file for performance testing."""
    fd, path = tempfile.mkstemp(suffix=".log")
    os.close(fd)

    logger = logging.getLogger("perf_test")
    logger.setLevel(logging.INFO)
    handler = ImmutableFileHandler(path)
    logger.addHandler(handler)

    for i in range(10000):
        logger.info(f"Performance test log entry {i + 1}")

    handler.close()
    logger.removeHandler(handler)

    yield path

    if os.path.exists(path):
        os.unlink(path)


@pytest.mark.slow
class TestPerformance:
    """Performance tests."""

    def test_stream_performance(self, large_log_file, benchmark):
        """Test streaming performance."""

        def stream_1000_lines():
            streamer = ValidatingLogStreamer(large_log_file)
            lines = list(streamer.stream_lines(0, 1000))
            return len(lines)

        result = benchmark(stream_1000_lines)
        assert result == 1000

    def test_memory_usage(self, large_log_file):
        """Test memory usage stays reasonable."""
        import tracemalloc

        tracemalloc.start()

        streamer = ValidatingLogStreamer(large_log_file)
        for _ in streamer.stream_lines(0, 5000):
            pass

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        assert peak < 100 * 1024 * 1024

    def test_large_file_streaming(self, large_log_file):
        """Test streaming large file."""
        streamer = ValidatingLogStreamer(large_log_file)

        start = time.time()
        count = 0
        for _ in streamer.stream_lines(0, 10000):
            count += 1
        elapsed = time.time() - start

        assert count == 10000
        assert count / elapsed > 1000
