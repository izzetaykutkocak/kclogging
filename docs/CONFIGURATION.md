# Configuration Guide

Complete guide to configuring the Immutable Log Widget.

## Basic Configuration

Minimal configuration requires only the log file path:

```python
from immutable_log_widget import ImmutableLogWidgetConfig

config = ImmutableLogWidgetConfig(
    log_file_path="/var/log/myapp.log"
)
```

## All Configuration Options

```python
config = ImmutableLogWidgetConfig(
    # Required
    log_file_path="/var/log/myapp.log",
    
    # URL Configuration
    url_prefix="/logs",
    
    # Security
    auth_decorator=my_auth_function,
    require_roles=['admin', 'viewer'],
    
    # Performance
    chunk_size=1000,
    max_file_size_mb=1000,
    
    # Features
    enable_download=True,
    enable_verification=True,
    auto_verify_on_load=False,
    
    # Advanced
    custom_css="/path/to/custom.css",
    custom_js="/path/to/custom.js"
)
```

## Configuration Recipes

### Development Configuration

```python
config = ImmutableLogWidgetConfig(
    log_file_path="./dev.log",
    enable_download=True,
    enable_verification=True,
    chunk_size=100  # Smaller chunks for testing
)
```

### Production Configuration

```python
from immutable_log_widget.utils.security import flask_login_required

config = ImmutableLogWidgetConfig(
    log_file_path="/var/log/production.log",
    auth_decorator=flask_login_required,
    enable_download=False,  # Disable downloads in production
    chunk_size=1000,
    max_file_size_mb=5000
)
```

### High-Security Configuration

```python
from immutable_log_widget.utils.security import flask_login_role_required

admin_only = flask_login_role_required(['admin'])

config = ImmutableLogWidgetConfig(
    log_file_path="/var/log/sensitive.log",
    auth_decorator=admin_only,
    enable_download=False,
    enable_verification=True,
    max_file_size_mb=1000
)
```

### High-Performance Configuration

```python
config = ImmutableLogWidgetConfig(
    log_file_path="/var/log/large.log",
    chunk_size=5000,  # Larger chunks for better performance
    enable_verification=False,  # Disable auto-validation
    max_file_size_mb=10000  # Allow very large files
)
```

## Troubleshooting

### File Not Found

**Error:** `FileNotFoundError: Log file not found`

**Solution:** Ensure the log file path is absolute and the file exists:
```python
import os
log_path = os.path.abspath("./app.log")
config = ImmutableLogWidgetConfig(log_file_path=log_path)
```

### Permission Denied

**Error:** `PermissionError: Log file not readable`

**Solution:** Check file permissions:
```bash
chmod 644 /var/log/myapp.log
```

### Invalid Chunk Size

**Error:** `ValueError: chunk_size must be between 100 and 10000`

**Solution:** Use a valid chunk size:
```python
config = ImmutableLogWidgetConfig(
    log_file_path="/var/log/app.log",
    chunk_size=1000  # Valid range: 100-10000
)
```
