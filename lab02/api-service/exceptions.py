class UserAlreadyExistsException(Exception):
    def __init__(self, login: str, email: str):
        super().__init__(f"User with login {login} or email {email} already exists")

class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        super().__init__(f"User with id {user_id} not found")

class LoginUnableException(Exception):
    def __init__(self):
        super().__init__("Login unable")

class ExpiredRefreshTokenException(Exception):
    def __init__(self):
        super().__init__(f"Refresh token has expired")

class InternalException(Exception):
    def __init__(self):
        super().__init__("Internal error")
