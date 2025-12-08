import logging
import hashlib
import json
import time

logger = logging.getLogger('test')
logger.setLevel(logging.INFO)

record = logger.makeRecord('test', logging.INFO, 'test.py', 1, 'Application started', (), None)

from logging import Formatter
formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
message = formatter.format(record)

print('Message:', message)
print('Timestamp (record.created):', record.created)
print('Levelno:', record.levelno)

from datetime import datetime
timestamp_str = message.split(' - ')[0]
print('Timestamp string:', timestamp_str)
dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
print('Parsed datetime:', dt)
timestamp_mktime = time.mktime(dt.timetuple()) + dt.microsecond / 1000000.0
print('Timestamp (mktime):', timestamp_mktime)
print('Match:', abs(record.created - timestamp_mktime) < 0.001)

block_data = {
    "prev_hash": "0" * 64,
    "message": message,
    "timestamp": record.created,
    "levelno": record.levelno
}

block_json = json.dumps(block_data, sort_keys=True)
print('\nBlock JSON:', block_json)
current_hash = hashlib.sha256(block_json.encode('utf-8')).hexdigest()
print('Hash (with record.created):', current_hash)

block_data2 = {
    "prev_hash": "0" * 64,
    "message": message,
    "timestamp": timestamp_mktime,
    "levelno": record.levelno
}

block_json2 = json.dumps(block_data2, sort_keys=True)
print('\nBlock JSON2:', block_json2)
current_hash2 = hashlib.sha256(block_json2.encode('utf-8')).hexdigest()
print('Hash (with mktime):', current_hash2)
