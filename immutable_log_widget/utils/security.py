#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security utilities for the Immutable Log Widget.

Provides decorators and helpers for integrating with various
authentication and authorization systems.
"""

from functools import wraps
from flask import session, request, jsonify
from typing import Callable, List, Optional, Union


def require_auth(f: Callable) -> Callable:
    """
    Basic authentication decorator using Flask session.

    Checks if user is authenticated by looking for 'user_id' in session.
    Returns 401 Unauthorized if not authenticated.

    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            return "Protected content"

    Args:
        f: Function to decorate

    Returns:
        Decorated function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return (
                jsonify(
                    {
                        "error": "Authentication required",
                        "message": "Please log in to access this resource",
                    }
                ),
                401,
            )
        return f(*args, **kwargs)

    return decorated_function


def require_role(roles: Union[str, List[str]]) -> Callable:
    """
    Role-based authorization decorator.

    Checks if the authenticated user has one of the required roles.
    Expects 'user_roles' to be stored in session as a list.

    Usage:
        @app.route('/admin')
        @require_role(['admin', 'superuser'])
        def admin_route():
            return "Admin content"

    Args:
        roles: Single role string or list of acceptable roles

    Returns:
        Decorator function
    """
    if isinstance(roles, str):
        roles = [roles]

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return (
                    jsonify(
                        {
                            "error": "Authentication required",
                            "message": "Please log in to access this resource",
                        }
                    ),
                    401,
                )

            user_roles = session.get("user_roles", [])
            if not any(role in user_roles for role in roles):
                return (
                    jsonify(
                        {
                            "error": "Insufficient permissions",
                            "message": f'This resource requires one of: {", ".join(roles)}',
                        }
                    ),
                    403,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def create_auth_decorator(auth_func: Callable) -> Callable:
    """
    Create a custom authentication decorator from a user-provided function.

    The auth_func should return True if authenticated, False otherwise.
    It can also raise exceptions or return Flask responses.

    Usage:
        def my_auth_check():
            return current_user.is_authenticated

        custom_auth = create_auth_decorator(my_auth_check)

        @app.route('/protected')
        @custom_auth
        def protected_route():
            return "Protected content"

    Args:
        auth_func: Function that checks authentication

    Returns:
        Decorator function
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = auth_func()

                if hasattr(result, "status_code"):
                    return result

                if result is False:
                    return (
                        jsonify({"error": "Authentication required", "message": "Access denied"}),
                        401,
                    )

                return f(*args, **kwargs)

            except Exception as e:
                return jsonify({"error": "Authentication error", "message": str(e)}), 401

        return decorated_function

    return decorator


def flask_login_required(f: Callable) -> Callable:
    """
    Decorator for Flask-Login integration.

    Requires Flask-Login to be installed and configured.

    Usage:
        from flask_login import LoginManager

        login_manager = LoginManager()
        login_manager.init_app(app)

        @app.route('/protected')
        @flask_login_required
        def protected_route():
            return "Protected content"

    Args:
        f: Function to decorate

    Returns:
        Decorated function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            from flask_login import current_user

            if not current_user.is_authenticated:
                return (
                    jsonify(
                        {
                            "error": "Authentication required",
                            "message": "Please log in to access this resource",
                        }
                    ),
                    401,
                )

            return f(*args, **kwargs)

        except ImportError:
            raise ImportError(
                "Flask-Login is required for flask_login_required decorator. "
                "Install it with: pip install Flask-Login"
            )

    return decorated_function


def flask_login_role_required(roles: Union[str, List[str]]) -> Callable:
    """
    Role-based decorator for Flask-Login.

    Assumes User model has a 'roles' attribute or 'has_role()' method.

    Usage:
        @app.route('/admin')
        @flask_login_role_required(['admin'])
        def admin_route():
            return "Admin content"

    Args:
        roles: Single role string or list of acceptable roles

    Returns:
        Decorator function
    """
    if isinstance(roles, str):
        roles = [roles]

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                from flask_login import current_user

                if not current_user.is_authenticated:
                    return jsonify({"error": "Authentication required"}), 401

                user_has_role = False

                if hasattr(current_user, "has_role"):
                    user_has_role = any(current_user.has_role(role) for role in roles)
                elif hasattr(current_user, "roles"):
                    user_roles = [
                        r.name if hasattr(r, "name") else str(r) for r in current_user.roles
                    ]
                    user_has_role = any(role in user_roles for role in roles)

                if not user_has_role:
                    return (
                        jsonify(
                            {
                                "error": "Insufficient permissions",
                                "message": f'Required roles: {", ".join(roles)}',
                            }
                        ),
                        403,
                    )

                return f(*args, **kwargs)

            except ImportError:
                raise ImportError("Flask-Login is required")

        return decorated_function

    return decorator


def jwt_required(f: Callable) -> Callable:
    """
    Decorator for Flask-JWT-Extended integration.

    Requires Flask-JWT-Extended to be installed and configured.

    Usage:
        from flask_jwt_extended import JWTManager

        jwt = JWTManager(app)

        @app.route('/protected')
        @jwt_required
        def protected_route():
            return "Protected content"

    Args:
        f: Function to decorate

    Returns:
        Decorated function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            from flask_jwt_extended import verify_jwt_in_request

            verify_jwt_in_request()
            return f(*args, **kwargs)

        except ImportError:
            raise ImportError(
                "Flask-JWT-Extended is required for jwt_required decorator. "
                "Install it with: pip install Flask-JWT-Extended"
            )

    return decorated_function


def api_key_required(
    header_name: str = "X-API-Key", valid_keys: Optional[List[str]] = None
) -> Callable:
    """
    Simple API key authentication decorator.

    Checks for API key in request headers.

    Usage:
        @app.route('/api/data')
        @api_key_required(valid_keys=['secret-key-1', 'secret-key-2'])
        def api_route():
            return "API data"

    Args:
        header_name: Name of the header containing the API key
        valid_keys: List of valid API keys (if None, any key is accepted)

    Returns:
        Decorator function
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get(header_name)

            if not api_key:
                return (
                    jsonify(
                        {
                            "error": "API key required",
                            "message": f"Please provide API key in {header_name} header",
                        }
                    ),
                    401,
                )

            if valid_keys and api_key not in valid_keys:
                return (
                    jsonify(
                        {"error": "Invalid API key", "message": "The provided API key is not valid"}
                    ),
                    401,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def ip_whitelist_required(allowed_ips: List[str]) -> Callable:
    """
    IP whitelist decorator.

    Only allows requests from specified IP addresses.

    Usage:
        @app.route('/internal')
        @ip_whitelist_required(['127.0.0.1', '192.168.1.0/24'])
        def internal_route():
            return "Internal content"

    Args:
        allowed_ips: List of allowed IP addresses or CIDR ranges

    Returns:
        Decorator function
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr

            if client_ip not in allowed_ips:
                return (
                    jsonify(
                        {"error": "Access denied", "message": "Your IP address is not authorized"}
                    ),
                    403,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator
