import re


def validate_name(name):
    """
    Validates that the name contains at least a first and last name.
    Returns True if valid, False otherwise.
    """
    # Check if name has at least two parts (first & last name)
    parts = name.strip().split()
    if len(parts) < 2:
        return False

    # Check if name contains only letters, spaces, hyphens, and apostrophes
    pattern = r'^[A-Za-z\s\-\']+$'
    return bool(re.match(pattern, name))


def validate_email(email):
    """
    Validates email format using regex.
    Returns True if valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """
    Validates international phone number format.
    Returns True if valid, False otherwise.
    """
    # Pattern for international phone numbers with country code
    # Allows formats like +1-555-123-4567, +44 7911 123456, etc.
    pattern = r'^\+\d{1,4}[-\s]?(\d{1,3}[-\s]?){1,4}\d{1,4}$'
    return bool(re.match(pattern, phone))


def sanitize_input(input_string):
    """
    Sanitizes input by removing potentially harmful characters.
    Returns sanitized string.
    """
    # Remove HTML tags
    sanitized = re.sub(r'<[^>]*>', '', input_string)

    # Remove special characters that could be used for injection
    sanitized = re.sub(r'[\'";`$\\]', '', sanitized)

    return sanitized.strip()