import hashlib
import json


def verify_log_integrity(file_path):
    GENESIS_HASH = '0' * 64
    expected_prev_hash = GENESIS_HASH

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            line_number = 0
            while True:
                log_line = f.readline()
                if not log_line:
                    break

                line_number += 1
                log_line = log_line.strip()

                if not log_line:
                    continue

                if log_line.startswith('BLOCK_DATA:'):
                    continue

                parts = log_line.split('|')
                if len(parts) != 3:
                    return (False, line_number)

                prev_hash_in_file, message, current_hash_in_file = parts

                if prev_hash_in_file != expected_prev_hash:
                    return (False, line_number)

                block_data_line = f.readline()
                line_number += 1

                if not block_data_line.startswith('BLOCK_DATA:'):
                    return (False, line_number)

                block_json = block_data_line[11:].strip()

                try:
                    block_data = json.loads(block_json)
                except json.JSONDecodeError:
                    return (False, line_number)

                recalculated_hash = hashlib.sha256(block_json.encode('utf-8')).hexdigest()

                if recalculated_hash != current_hash_in_file:
                    return (False, line_number - 1)

                if block_data.get('prev_hash') != expected_prev_hash:
                    return (False, line_number - 1)

                if block_data.get('message') != message:
                    return (False, line_number - 1)

                expected_prev_hash = current_hash_in_file

        return True

    except FileNotFoundError:
        return (False, 0)
    except Exception:
        return (False, -1)