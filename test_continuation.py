import logging
import os
from immutable_handler import ImmutableFileHandler
from verify_log import verify_log_integrity

log_file = 'continuation_test.log'

if os.path.exists(log_file):
    os.remove(log_file)

print("=== Session 1: Creating initial log ===")
logger1 = logging.getLogger('session1')
logger1.setLevel(logging.DEBUG)
logger1.handlers.clear()

handler1 = ImmutableFileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler1.setFormatter(formatter)
logger1.addHandler(handler1)

logger1.info("Session 1: First message")
logger1.debug("Session 1: Second message")
logger1.warning("Session 1: Third message")

print(f"Last hash after session 1: {handler1.last_hash}")
handler1.close()

print("\n=== Session 2: Continuing the log ===")
logger2 = logging.getLogger('session2')
logger2.setLevel(logging.DEBUG)
logger2.handlers.clear()

handler2 = ImmutableFileHandler(log_file)
handler2.setFormatter(formatter)
logger2.addHandler(handler2)

print(f"Loaded last hash: {handler2.last_hash}")
print(f"Hashes match: {handler1.last_hash == handler2.last_hash}")

logger2.error("Session 2: Fourth message")
logger2.critical("Session 2: Fifth message")

handler2.close()

print("\n=== Verifying complete log integrity ===")
result = verify_log_integrity(log_file)

if result is True:
    print("✓ Log integrity verified successfully!")
    print("✓ Continuation works correctly!")
else:
    print(f"✗ Log integrity check failed at line {result[1]}")

print("\n=== Log contents ===")
with open(log_file, 'r') as f:
    for i, line in enumerate(f, 1):
        if not line.startswith('BLOCK_DATA:'):
            print(f"Line {i}: {line.strip()[:80]}...")
