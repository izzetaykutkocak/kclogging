#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes

Flask routes for the immutable log widget.
"""

import os
import time
from flask import render_template, jsonify, send_file, request, current_app
from functools import wraps
from typing import Callable, Optional

from .streaming import LogStreamer, ValidatingLogStreamer
from ..core.integrity_checker import LogIntegrityChecker


def apply_auth(auth_decorator: Optional[Callable]):
    """
    Apply authentication decorator if provided, otherwise return pass-through.

    Args:
        auth_decorator: Optional authentication decorator

    Returns:
        Decorator function
    """
    if auth_decorator:
        return auth_decorator

    def no_auth(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)

        return decorated_function

    return no_auth


def register_routes(bp, config):
    """
    Register all routes on the blueprint.

    Args:
        bp: Flask Blueprint instance
        config: WidgetConfig instance
    """

    @bp.route("/view")
    @apply_auth(config.auth_decorator)
    def view_logs():
        """
        Render the log viewer page.

        Returns:
            HTML: Rendered log viewer template
        """
        try:
            streamer = LogStreamer(config.log_file_path)

            context = {
                "filename": os.path.basename(config.log_file_path),
                "total_lines": streamer.get_total_lines(),
                "file_size": streamer.get_file_size_human(),
                "enable_download": config.enable_download,
                "api_base_url": bp.url_prefix,
            }

            return render_template("log_viewer.html", **context)

        except FileNotFoundError:
            return jsonify({"error": "Log file not found", "file": config.log_file_path}), 404

        except PermissionError:
            return jsonify({"error": "Permission denied", "file": config.log_file_path}), 403

        except Exception as e:
            return jsonify({"error": "Internal server error", "message": str(e)}), 500

    @bp.route("/api/stream")
    @apply_auth(config.auth_decorator)
    def stream_logs():
        """
        Stream log lines with pagination and validation.

        Query Parameters:
            start (int): Starting line number (0-indexed, default: 0)
            count (int): Number of lines to return (default: 1000, max: 5000)
            validate (bool): Whether to validate hashes (default: true)

        Returns:
            JSON: {
                "lines": [
                    {
                        "line_number": int,
                        "content": str,
                        "hash": str,
                        "is_valid": bool,
                        "log_level": str
                    },
                    ...
                ],
                "has_more": bool,
                "total_lines": int,
                "start": int,
                "count": int
            }
        """
        try:
            start = int(request.args.get("start", 0))
            count = int(request.args.get("count", config.chunk_size))
            validate = request.args.get("validate", "true").lower() == "true"

            if start < 0:
                return jsonify({"error": "start must be >= 0"}), 400

            if count < 1:
                return jsonify({"error": "count must be >= 1"}), 400

            max_count = 5000
            if count > max_count:
                count = max_count

            if validate:
                streamer = ValidatingLogStreamer(config.log_file_path, config.chunk_size)
            else:
                streamer = LogStreamer(config.log_file_path, config.chunk_size)

            total_lines = streamer.get_total_lines()
            end = min(start + count, total_lines)

            lines = []
            for line_data in streamer.stream_lines(start_line=start, end_line=end):
                lines.append(line_data)

            has_more = end < total_lines

            return jsonify(
                {
                    "lines": lines,
                    "has_more": has_more,
                    "total_lines": total_lines,
                    "start": start,
                    "count": len(lines),
                }
            )

        except ValueError as e:
            return jsonify({"error": f"Invalid parameter: {str(e)}"}), 400

        except FileNotFoundError:
            return jsonify({"error": "Log file not found"}), 404

        except Exception as e:
            current_app.logger.error(f"Error streaming logs: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    @bp.route("/api/download")
    @apply_auth(config.auth_decorator)
    def download_log():
        """
        Download the complete log file.

        Returns:
            File: Log file as attachment

        Status Codes:
            200: Success
            403: Download disabled
            404: File not found
            500: Internal error
        """
        try:
            if not config.enable_download:
                return (
                    jsonify(
                        {
                            "error": "Download is disabled",
                            "message": "Log file downloads have been disabled by the administrator",
                        }
                    ),
                    403,
                )

            if not os.path.exists(config.log_file_path):
                return jsonify({"error": "Log file not found"}), 404

            filename = os.path.basename(config.log_file_path)

            return send_file(
                config.log_file_path,
                as_attachment=True,
                download_name=filename,
                mimetype="text/plain",
            )

        except PermissionError:
            return jsonify({"error": "Permission denied"}), 403

        except Exception as e:
            current_app.logger.error(f"Error downloading log: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    @bp.route("/api/verify", methods=["POST"])
    @apply_auth(config.auth_decorator)
    def verify_integrity():
        """
        Verify the integrity of the entire log file.

        This may take significant time for large files.

        Returns:
            JSON: {
                "valid": bool,
                "total_lines": int,
                "tampered_lines": [int],
                "check_duration_ms": float,
                "file_size": str
            }

        Status Codes:
            200: Verification complete (check 'valid' field for result)
            404: File not found
            500: Internal error
        """
        try:
            start_time = time.time()

            checker = LogIntegrityChecker(config.log_file_path)

            result = checker.verify_full_log()

            duration_ms = (time.time() - start_time) * 1000

            streamer = LogStreamer(config.log_file_path)
            file_size = streamer.get_file_size_human()

            result["check_duration_ms"] = round(duration_ms, 2)
            result["file_size"] = file_size

            return jsonify(result)

        except FileNotFoundError:
            return jsonify({"error": "Log file not found"}), 404

        except Exception as e:
            current_app.logger.error(f"Error verifying log: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
