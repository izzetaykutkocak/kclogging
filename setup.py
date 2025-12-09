#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for immutable-log-widget package.
"""

import os
from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="immutable-log-widget",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Flask widget for immutable log file viewing with integrity validation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/immutable-log-widget",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/immutable-log-widget/issues",
        "Documentation": "https://github.com/yourusername/immutable-log-widget/blob/main/docs/",
        "Source Code": "https://github.com/yourusername/immutable-log-widget",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    include_package_data=True,
    package_data={
        "immutable_log_widget": [
            "static/css/*.css",
            "static/js/*.js",
            "templates/*.html",
        ],
    },
    install_requires=[
        "Flask>=2.0.0",
        "werkzeug>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "pytest-benchmark>=3.4.0",
            "memory-profiler>=0.60.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "security": [
            "Flask-Login>=0.5.0",
            "Flask-Security-Too>=4.0.0",
            "Flask-JWT-Extended>=4.0.0",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="flask logging immutable integrity validation security audit",
)
