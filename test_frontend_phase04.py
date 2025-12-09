#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Frontend - Phase 04

Test the frontend implementation with a sample log file.
"""

import os
import sys
from flask import Flask
from immutable_log_widget import create_blueprint

def create_test_app():
    """Create a test Flask application with the log viewer."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key-for-phase-04'
    
    test_log_file = 'test.log'
    if not os.path.exists(test_log_file):
        print(f"Creating test log file: {test_log_file}")
        with open(test_log_file, 'w') as f:
            f.write("2024-01-01 10:00:00 INFO Application started\n")
            f.write("2024-01-01 10:00:01 DEBUG Loading configuration\n")
            f.write("2024-01-01 10:00:02 INFO Configuration loaded successfully\n")
            f.write("2024-01-01 10:00:03 WARN Deprecated feature used\n")
            f.write("2024-01-01 10:00:04 ERROR Connection failed\n")
            f.write("2024-01-01 10:00:05 INFO Retrying connection\n")
            f.write("2024-01-01 10:00:06 INFO Connection established\n")
            f.write("2024-01-01 10:00:07 DEBUG Processing request\n")
            f.write("2024-01-01 10:00:08 INFO Request processed successfully\n")
            f.write("2024-01-01 10:00:09 INFO Application running\n")
    
    bp = create_blueprint(
        log_file_path=test_log_file,
        url_prefix='/logs',
        enable_download=True,
        auth_decorator=None
    )
    
    app.register_blueprint(bp)
    
    @app.route('/')
    def index():
        return '''
        <html>
        <head>
            <title>Phase 04 Frontend Test</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                }
                h1 { color: #007bff; }
                .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .btn {
                    display: inline-block;
                    padding: 10px 20px;
                    background: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px 5px;
                }
                .btn:hover { background: #0056b3; }
                ul { line-height: 1.8; }
            </style>
        </head>
        <body>
            <h1>🎉 Phase 04 Frontend Development - Test Page</h1>
            
            <div class="info">
                <h2>Frontend Components Created:</h2>
                <ul>
                    <li>✅ HTML Template (log_viewer.html)</li>
                    <li>✅ CSS Styling (widget.css)</li>
                    <li>✅ JavaScript Client (widget.js)</li>
                </ul>
            </div>
            
            <h2>Test the Log Viewer:</h2>
            <a href="/logs/view" class="btn">Open Log Viewer</a>
            
            <h2>Features to Test:</h2>
            <ul>
                <li>Initial log loading</li>
                <li>Infinite scroll (scroll down to load more)</li>
                <li>Verify Integrity button</li>
                <li>Download Log button</li>
                <li>Refresh button</li>
                <li>Color-coded log levels (ERROR, WARN, INFO, DEBUG)</li>
                <li>Responsive design (resize browser window)</li>
                <li>Dark mode (change system theme)</li>
            </ul>
            
            <h2>API Endpoints:</h2>
            <ul>
                <li><a href="/logs/api/stream?start=0&count=10">/logs/api/stream</a> - Stream logs</li>
                <li><a href="/logs/api/download">/logs/api/download</a> - Download log file</li>
                <li>POST /logs/api/verify - Verify integrity</li>
            </ul>
        </body>
        </html>
        '''
    
    return app

if __name__ == '__main__':
    app = create_test_app()
    print("\n" + "="*60)
    print("Phase 04 Frontend Development - Test Server")
    print("="*60)
    print("\nServer starting at: http://127.0.0.1:5000")
    print("\nTest URLs:")
    print("  - Home Page:    http://127.0.0.1:5000/")
    print("  - Log Viewer:   http://127.0.0.1:5000/logs/view")
    print("  - API Stream:   http://127.0.0.1:5000/logs/api/stream")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
