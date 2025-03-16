class ExpiredRefreshTokenException(Exception):
    def __init__(self):
        super().__init__(f"Refresh token has expired")
