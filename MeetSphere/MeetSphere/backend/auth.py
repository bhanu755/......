from backend.database import check_login, register_user


def authenticate_user(username: str, password: str):
    """Verify username and password against the database."""
    return check_login(username, password)


def create_user(name: str, email: str, username: str, password: str):
    """Create a new user account in the database."""
    return register_user(name, email, username, password)
