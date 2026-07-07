from .auth_state import get_auth_flag


def authentication_status() -> str:
    """
    Returns the current authentication status.
    """
    return get_auth_flag()