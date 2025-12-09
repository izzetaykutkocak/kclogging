# Immutable Log Widget Examples

This directory contains example applications demonstrating how to integrate the Immutable Log Widget into Flask applications.

## Examples

### 1. Basic Integration (`basic_integration.py`)

The simplest possible integration with minimal configuration.

**Features:**
- No authentication required
- Default settings
- Sample log generation
- Direct initialization pattern

**Usage:**
```bash
source venv/bin/activate
python examples/basic_integration.py
```

Then visit: http://localhost:5000

**Key Code:**
```python
from immutable_log_widget import ImmutableLogWidget, ImmutableLogWidgetConfig

config = ImmutableLogWidgetConfig(
    log_file_path=LOG_FILE,
    enable_download=True,
    chunk_size=1000
)

widget = ImmutableLogWidget(app, config)
```

### 2. Secure Integration (`secure_integration.py`)

Demonstrates integration with Flask-Login for authentication.

**Features:**
- User authentication with Flask-Login
- Role-based access control
- Protected log viewing
- Login/logout functionality

**Requirements:**
```bash
pip install Flask-Login
```

**Usage:**
```bash
source venv/bin/activate
python examples/secure_integration.py
```

**Login Credentials:**
- Admin: username=`admin`, password=`admin123`
- User: username=`user`, password=`user123`

**Key Code:**
```python
from immutable_log_widget.utils.security import flask_login_required

config = ImmutableLogWidgetConfig(
    log_file_path=LOG_FILE,
    auth_decorator=flask_login_required,
    enable_download=True
)

widget = ImmutableLogWidget(app, config)
```

## Common Patterns

### Direct Initialization
```python
app = Flask(__name__)
config = ImmutableLogWidgetConfig(log_file_path="/path/to/app.log")
widget = ImmutableLogWidget(app, config)
```

### Factory Pattern
```python
widget = ImmutableLogWidget()

def create_app():
    app = Flask(__name__)
    config = ImmutableLogWidgetConfig(log_file_path="/path/to/app.log")
    widget.init_app(app, config)
    return app
```

### Using the Log Handler
```python
import logging

logger = logging.getLogger('myapp')
handler = widget.get_log_handler()
logger.addHandler(handler)
```

### Programmatic Integrity Verification
```python
result = widget.verify_integrity()
if result['valid']:
    print("Log is valid!")
else:
    print(f"Found {len(result['tampered_lines'])} tampered lines")
```

## Configuration Options

All examples use `ImmutableLogWidgetConfig` with these options:

- `log_file_path` (required): Path to the log file
- `url_prefix` (optional): URL prefix for the widget routes (default: `/immutable_logs`)
- `auth_decorator` (optional): Authentication decorator function
- `chunk_size` (optional): Number of lines to load per request (default: 1000)
- `enable_download` (optional): Allow log file download (default: False)

## Notes

- All examples use the development server (`app.run(debug=True)`)
- For production, use a WSGI server like Gunicorn or uWSGI
- The log files are created in the `examples/` directory
- Examples automatically add the parent directory to `sys.path` for imports
