"""
Authentication exception.
"""


class AuthenticationException(Exception):
    def __init__(self, description: str = "Unauthorized"):
        self.message = "Unauthorized"
        self.description = description
        super().__init__(self.message)
