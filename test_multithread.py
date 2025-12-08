import logging
import threading
import time
import random
from immutable_handler import ImmutableFileHandler
from verify_log import verify_log_integrity
import os

log_file = 'multithread_test.log'

if os.path.exists(log_file):
    os.remove(log_file)

logger = logging.getLogger('multithread_test')
logger.setLevel(logging.DEBUG)
logger.handlers.clear()

handler = ImmutableFileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

results = {'success': 0, 'failed': 0}
results_lock = threading.Lock()

def worker(thread_id, num_messages):
    try:
        for i in range(num_messages):
            level = random.choice([logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL])
            logger.log(level, f"Thread {thread_id} - Message {i+1}")
            time.sleep(random.uniform(0.0001, 0.001))
        
        with results_lock:
            results['success'] += 1
    except Exception as e:
        print(f"Thread {thread_id} failed: {e}")
        with results_lock:
            results['failed'] += 1

num_threads = 100
messages_per_thread = 10

print(f"=== Multi-thread Test ===")
print(f"Threads: {num_threads}")
print(f"Messages per thread: {messages_per_thread}")
print(f"Total expected messages: {num_threads * messages_per_thread}")
print("\nStarting threads...")

start_time = time.time()

threads = []
for i in range(num_threads):
    t = threading.Thread(target=worker, args=(i, messages_per_thread))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

end_time = time.time()

handler.close()

print(f"\n=== Results ===")
print(f"Threads completed successfully: {results['success']}")
print(f"Threads failed: {results['failed']}")
print(f"Time taken: {end_time - start_time:.2f} seconds")

with open(log_file, 'r') as f:
    log_lines = [line for line in f if not line.startswith('BLOCK_DATA:')]
    print(f"Total log entries written: {len(log_lines)}")

print("\n=== Verifying log integrity ===")
result = verify_log_integrity(log_file)

if result is True:
    print("✓ Log integrity verified successfully!")
    print("✓ Thread-safe implementation works correctly!")
else:
    print(f"✗ Log integrity check failed at line {result[1]}")

print("\n=== First 5 log entries ===")
with open(log_file, 'r') as f:
    count = 0
    for line in f:
        if not line.startswith('BLOCK_DATA:'):
            print(f"{line.strip()[:100]}...")
            count += 1
            if count >= 5:
                break

print("\n=== Last 5 log entries ===")
with open(log_file, 'r') as f:
    log_lines = [line for line in f if not line.startswith('BLOCK_DATA:')]
    for line in log_lines[-5:]:
        print(f"{line.strip()[:100]}...")
