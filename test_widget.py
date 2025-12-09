#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for ImmutableLogWidget"""

from flask import Flask
from immutable_log_widget import ImmutableLogWidget, ImmutableLogWidgetConfig
import tempfile
import os

print("=" * 60)
print("Testing ImmutableLogWidget")
print("=" * 60)

with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
    log_file = f.name
    f.write('Test log line\n')

try:
    print("\n1. Testing direct initialization...")
    app = Flask(__name__)
    app.secret_key = 'test-key'
    
    config = ImmutableLogWidgetConfig(log_file_path=log_file)
    widget = ImmutableLogWidget(app, config)
    
    assert widget.is_initialized, "Widget should be initialized"
    print("   ✓ Direct initialization successful")
    print(f"   ✓ Widget initialized: {widget.is_initialized}")
    print(f"   ✓ Viewer URL: {widget.get_viewer_url()}")
    
    print("\n2. Testing API URLs...")
    urls = widget.get_api_urls()
    assert 'view' in urls, "Should have view URL"
    assert 'stream' in urls, "Should have stream URL"
    assert 'download' in urls, "Should have download URL"
    assert 'verify' in urls, "Should have verify URL"
    print(f"   ✓ View: {urls['view']}")
    print(f"   ✓ Stream: {urls['stream']}")
    print(f"   ✓ Download: {urls['download']}")
    print(f"   ✓ Verify: {urls['verify']}")
    
    print("\n3. Testing factory pattern...")
    widget2 = ImmutableLogWidget()
    assert not widget2.is_initialized, "Widget should not be initialized yet"
    print(f"   ✓ Factory pattern - not initialized: {not widget2.is_initialized}")
    
    app2 = Flask(__name__)
    app2.secret_key = 'test-key-2'
    widget2.init_app(app2, config)
    assert widget2.is_initialized, "Widget should be initialized after init_app"
    print(f"   ✓ Factory pattern - initialized: {widget2.is_initialized}")
    
    print("\n4. Testing get_log_handler...")
    handler = widget.get_log_handler()
    assert handler is not None, "Handler should not be None"
    print(f"   ✓ Log handler created: {type(handler).__name__}")
    
    print("\n5. Testing __repr__...")
    repr_str = repr(widget)
    assert "initialized" in repr_str, "Repr should contain 'initialized'"
    print(f"   ✓ Widget repr: {repr_str}")
    
    print("\n6. Testing app extensions...")
    assert hasattr(app, 'extensions'), "App should have extensions"
    assert 'immutable_log_widget' in app.extensions, "Widget should be in extensions"
    print(f"   ✓ Widget registered in app.extensions")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    if os.path.exists(log_file):
        os.unlink(log_file)
