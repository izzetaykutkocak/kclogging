# API Documentation

Complete reference for the Immutable Log Widget API.

## Table of Contents

- [ImmutableLogWidget](#immutablelogwidget)
- [ImmutableLogWidgetConfig](#immutablelogwidgetconfig)
- [ImmutableFileHandler](#immutablefilehandler)
- [LogIntegrityChecker](#logintegritychecker)
- [Security Utilities](#security-utilities)

---

## ImmutableLogWidget

Main widget class for integrating log viewing into Flask applications.

### Constructor

```python
ImmutableLogWidget(app=None, config=None)
```

**Parameters:**
- `app` (Flask, optional): Flask application instance
- `config` (ImmutableLogWidgetConfig, optional): Widget configuration

**Example:**
```python
widget = ImmutableLogWidget(app, config)
```

### Methods

#### init_app(app, config)

Initialize the widget with a Flask application (factory pattern).

**Parameters:**
- `app` (Flask): Flask application instance
- `config` (ImmutableLogWidgetConfig): Widget configuration

**Raises:**
- `ValueError`: If app is not a Flask instance
- `TypeError`: If config is not ImmutableLogWidgetConfig

**Example:**
```python
widget = ImmutableLogWidget()
widget.init_app(app, config)
```

#### get_log_handler()

Get a configured ImmutableFileHandler for logging.

**Returns:**
- `ImmutableFileHandler`: Configured handler

**Example:**
```python
handler = widget.get_log_handler()
logger.addHandler(handler)
```

#### verify_integrity()

Programmatically verify log file integrity.

**Returns:**
- `dict`: Verification results
  - `valid` (bool): True if all lines are valid
  - `total_lines` (int): Total number of lines
  - `tampered_lines` (list): List of tampered line numbers

**Example:**
```python
result = widget.verify_integrity()
if result['valid']:
    print("Log is valid!")
```

#### get_viewer_url()

Get the URL for the log viewer page.

**Returns:**
- `str`: Relative URL to the viewer page

**Example:**
```python
url = widget.get_viewer_url()
print(f"View logs at: {url}")
```

#### get_api_urls()

Get all API endpoint URLs.

**Returns:**
- `dict`: Dictionary of endpoint names to URLs

**Example:**
```python
urls = widget.get_api_urls()
print(f"Stream API: {urls['stream']}")
```

---

## ImmutableLogWidgetConfig

Configuration class for the widget.

### Constructor

```python
ImmutableLogWidgetConfig(
    log_file_path,
    url_prefix="/immutable_logs",
    auth_decorator=None,
    require_roles=None,
    chunk_size=1000,
    max_file_size_mb=None,
    enable_download=True,
    enable_verification=True,
    auto_verify_on_load=False
)
```

**Parameters:**
- `log_file_path` (str, required): Absolute path to log file
- `url_prefix` (str): URL prefix for routes (default: "/immutable_logs")
- `auth_decorator` (callable): Authentication decorator (default: None)
- `require_roles` (list): Required roles for access (default: None)
- `chunk_size` (int): Lines per request (default: 1000, range: 100-10000)
- `max_file_size_mb` (int): Maximum file size in MB (default: None)
- `enable_download` (bool): Allow downloads (default: True)
- `enable_verification` (bool): Allow verification (default: True)
- `auto_verify_on_load` (bool): Auto-verify on load (default: False)

**Raises:**
- `ValueError`: If validation fails
- `FileNotFoundError`: If log file doesn't exist
- `PermissionError`: If log file isn't readable

**Example:**
```python
config = ImmutableLogWidgetConfig(
    log_file_path="/var/log/app.log",
    chunk_size=500,
    enable_download=False
)
```

---

## ImmutableFileHandler

Logging handler that writes logs with cryptographic hash chains.

### Constructor

```python
ImmutableFileHandler(filename, mode='a', encoding='utf-8')
```

**Parameters:**
- `filename` (str): Path to log file
- `mode` (str): File open mode (default: 'a')
- `encoding` (str): File encoding (default: 'utf-8')

**Example:**
```python
handler = ImmutableFileHandler('/var/log/app.log')
logger.addHandler(handler)
```

### Methods

#### get_last_hash()

Get the current last hash in the chain.

**Returns:**
- `str`: Last hash (64 character hex string)

#### get_file_path()

Get the absolute path to the log file.

**Returns:**
- `str`: Absolute file path

---

## LogIntegrityChecker

Validates log file integrity by verifying hash chains.

### Constructor

```python
LogIntegrityChecker(log_file_path)
```

**Parameters:**
- `log_file_path` (str): Path to log file

**Example:**
```python
checker = LogIntegrityChecker('/var/log/app.log')
```

### Methods

#### verify_full_log()

Verify the entire log file.

**Returns:**
- `dict`: Verification results
  - `valid` (bool): True if all lines are valid
  - `total_lines` (int): Total number of lines
  - `tampered_lines` (list): List of tampered line numbers
  - `error` (str or None): Error message if file can't be read

**Example:**
```python
result = checker.verify_full_log()
print(f"Valid: {result['valid']}")
print(f"Tampered lines: {result['tampered_lines']}")
```

---

## Security Utilities

Authentication and authorization decorators.

### flask_login_required

Decorator for Flask-Login integration.

**Example:**
```python
from immutable_log_widget.utils.security import flask_login_required

config = ImmutableLogWidgetConfig(
    log_file_path="/var/log/app.log",
    auth_decorator=flask_login_required
)
```

### create_auth_decorator(auth_func)

Create custom authentication decorator.

**Parameters:**
- `auth_func` (callable): Function that checks authentication

**Returns:**
- `callable`: Decorator function

**Example:**
```python
def my_auth():
    return current_user.is_authenticated

custom_auth = create_auth_decorator(my_auth)
```

### api_key_required(header_name='X-API-Key', valid_keys=None)

API key authentication decorator.

**Parameters:**
- `header_name` (str): Header name for API key
- `valid_keys` (list): List of valid API keys

**Returns:**
- `callable`: Decorator function

**Example:**
```python
api_auth = api_key_required(valid_keys=['secret-123'])
```

---

## REST API Endpoints

### GET /immutable_logs/view

Render the log viewer page.

**Response:** HTML page

### GET /immutable_logs/api/stream

Stream log lines with pagination.

**Query Parameters:**
- `start` (int): Starting line number (default: 0)
- `count` (int): Number of lines (default: 1000, max: 5000)
- `validate` (bool): Validate hashes (default: true)

**Response:**
```json
{
  "lines": [
    {
      "line_number": 1,
      "content": "log content",
      "hash": "abc123...",
      "is_valid": true,
      "log_level": "INFO"
    }
  ],
  "has_more": true,
  "total_lines": 10000,
  "start": 0,
  "count": 1000
}
```

### GET /immutable_logs/api/download

Download the complete log file.

**Response:** File attachment

### POST /immutable_logs/api/verify

Verify log file integrity.

**Response:**
```json
{
  "valid": true,
  "total_lines": 10000,
  "tampered_lines": [],
  "check_duration_ms": 1234.56,
  "file_size": "1.5 MB"
}
```
