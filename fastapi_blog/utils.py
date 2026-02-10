"""Utility functions for the FastAPI blog application."""

import re
import secrets
from pathlib import Path


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to make it safe for storage.

    - Strips leading/trailing whitespace
    - Removes or replaces unsafe characters
    - Prevents path traversal attacks
    - Ensures the filename is not empty

    Args:
        filename: The original filename

    Returns:
        A sanitized filename safe for storage

    Raises:
        ValueError: If the filename is empty or invalid after sanitization
    """
    # Strip whitespace
    filename = filename.strip()

    # Get the filename without any directory path (security)
    filename = Path(filename).name

    # Replace spaces with underscores first (more readable than removing them)
    filename = filename.replace(' ', '_')

    # Remove any non-alphanumeric characters except dots, hyphens, and underscores
    # This removes: /, \, and other special chars (prevents path traversal attacks)
    filename = re.sub(r'[^\w.-]', '', filename)

    # Remove any leading/trailing dots or hyphens (hidden files on Unix)
    filename = filename.strip('.-')

    if not filename:
        raise ValueError("Filename is empty after sanitization")

    return filename


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename by adding a random token to prevent collisions.

    Args:
        original_filename: The original filename

    Returns:
        A unique filename with the same extension

    Example:
        "profile.png" -> "abc123def456_profile.png"
    """
    sanitized = sanitize_filename(original_filename)
    name = Path(sanitized).stem
    extension = Path(sanitized).suffix

    # Generate a random token (8 hex characters)
    random_token = secrets.token_hex(4)

    return f"{random_token}_{name}{extension}"
