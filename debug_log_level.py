import tempfile
import logging
import os
from immutable_log_widget.core.immutable_handler import ImmutableFileHandler
from immutable_log_widget.web.streaming import ValidatingLogStreamer

fd, path = tempfile.mkstemp(suffix='.log')
os.close(fd)

logger = logging.getLogger('test_debug')
logger.setLevel(logging.INFO)
handler = ImmutableFileHandler(path)
logger.addHandler(handler)

logger.info('First log entry')
logger.warning('Second log entry')
logger.error('Third log entry')

handler.close()
logger.removeHandler(handler)

print('File contents:')
with open(path, 'r') as f:
    print(f.read())

streamer = ValidatingLogStreamer(path)
lines = list(streamer.stream_lines())
print('\nExtracted levels:')
for line in lines:
    print(f'Line {line["line_number"]}: level={line["log_level"]}, content={line["content"][:80]}')

os.unlink(path)
