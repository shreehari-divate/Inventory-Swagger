from flask import request
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def is_testing():
    """Check if we're in testing mode"""
    return os.getenv('TESTING') == 'True'

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    enabled=not is_testing()
)