"""Simple in-memory rate limiter using only the standard library."""
import time
from functools import wraps
from flask import request, jsonify

# { ip: [timestamp, timestamp, ...] }
_attempts: dict[str, list[float]] = {}


def rate_limit(max_attempts: int = 5, window_seconds: int = 60, message: str = "Demasiados intentos"):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr or "unknown"
            now = time.time()
            cutoff = now - window_seconds

            # Clean old entries
            if ip in _attempts:
                _attempts[ip] = [t for t in _attempts[ip] if t > cutoff]
            else:
                _attempts[ip] = []

            if len(_attempts[ip]) >= max_attempts:
                wait = int(_attempts[ip][0] + window_seconds - now) + 1
                return jsonify({"error": f"{message}. Intente de nuevo en {wait} segundos."}), 429

            _attempts[ip].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator
