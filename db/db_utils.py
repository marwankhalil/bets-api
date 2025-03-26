import uuid

def is_valid_uuid(value):
    """Helper function to check if a string is a valid UUID."""
    try:
        uuid.UUID(value, version=4)  # Checks if it's a valid UUIDv4
        return True
    except ValueError:
        return False