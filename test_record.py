import logging
from immutable_handler import ImmutableFileHandler

logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
handler = ImmutableFileHandler('test.log', mode='w')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

record = logger.makeRecord('test', logging.INFO, 'test.py', 1, 'Test message', (), None)
print('Timestamp:', record.created)
print('Levelno:', record.levelno)
print('Message:', handler.format(record))
