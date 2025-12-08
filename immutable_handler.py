import logging
import hashlib
import json
import os
import threading


class ImmutableFileHandler(logging.FileHandler):
    GENESIS_HASH = '0' * 64
    _lock = threading.Lock()

    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)
        self.last_hash = self.GENESIS_HASH
        self._load_last_hash()

    def _load_last_hash(self):
        if os.path.exists(self.baseFilename) and os.path.getsize(self.baseFilename) > 0:
            try:
                with open(self.baseFilename, 'r', encoding=self.encoding or 'utf-8') as f:
                    lines = f.readlines()
                    for i in range(len(lines) - 1, -1, -1):
                        line = lines[i].strip()
                        if line and not line.startswith('BLOCK_DATA:'):
                            parts = line.split('|')
                            if len(parts) == 3:
                                self.last_hash = parts[2]
                                break
            except Exception:
                pass

    def emit(self, record):
        with self._lock:
            try:
                message = self.format(record)

                block_data = {
                    "prev_hash": self.last_hash,
                    "message": message,
                    "timestamp": record.created,
                    "levelno": record.levelno
                }

                block_json = json.dumps(block_data, sort_keys=True)
                current_hash = hashlib.sha256(block_json.encode('utf-8')).hexdigest()

                log_line = f"{self.last_hash}|{message}|{current_hash}\n"

                if self.stream is None:
                    self.stream = self._open()

                self.stream.write(log_line)
                self.stream.write(f"BLOCK_DATA:{block_json}\n")
                self.flush()

                self.last_hash = current_hash

            except Exception:
                self.handleError(record)