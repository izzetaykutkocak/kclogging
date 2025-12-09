#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Flask App

Test application for the immutable log widget blueprint.
"""

from flask import Flask
from immutable_log_widget.web.blueprint import create_blueprint, WidgetConfig

app = Flask(__name__)

config = WidgetConfig(
    log_file_path="test.log",
    chunk_size=1000,
    enable_download=True
)

bp = create_blueprint(config)
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
