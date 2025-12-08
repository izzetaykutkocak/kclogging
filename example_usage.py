import logging
import os
from immutable_handler import ImmutableFileHandler
from verify_log import verify_log_integrity


def example_usage():
    log_file = 'immutable.log'
    
    if os.path.exists(log_file):
        os.remove(log_file)
    
    logger = logging.getLogger('immutable_logger')
    logger.setLevel(logging.DEBUG)
    
    handler = ImmutableFileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    print("Writing log messages...")
    logger.info("Application started")
    logger.debug("Debug information")
    logger.warning("This is a warning")
    logger.error("An error occurred")
    logger.critical("Critical system failure")
    
    print(f"\nLog file created: {log_file}")
    print("\nVerifying log integrity...")
    result = verify_log_integrity(log_file)
    
    if result is True:
        print("✓ Log integrity verified successfully!")
    else:
        print(f"✗ Log integrity check failed at line {result[1]}")
    
    print("\n" + "="*60)
    print("Demonstrating tampering detection...")
    print("="*60)
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    if len(lines) >= 4:
        lines[2] = lines[2].replace("Debug information", "TAMPERED MESSAGE")
        
        tampered_file = 'immutable_tampered.log'
        with open(tampered_file, 'w') as f:
            f.writelines(lines)
        
        print(f"\nTampered log file created: {tampered_file}")
        print("Verifying tampered log integrity...")
        result = verify_log_integrity(tampered_file)
        
        if result is True:
            print("✓ Log integrity verified successfully!")
        else:
            print(f"✗ Log integrity check failed at line {result[1]}")
        
        os.remove(tampered_file)
    
    print("\n" + "="*60)
    print("Log file contents (first 5 lines):")
    print("="*60)
    with open(log_file, 'r') as f:
        for i, line in enumerate(f, 1):
            if i > 5:
                break
            print(f"Line {i}: {line.strip()[:80]}...")


if __name__ == "__main__":
    example_usage()
