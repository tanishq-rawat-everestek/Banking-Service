"""
Authorization exception.
"""


class AuthorizationException(Exception):
    def __init__(self, description: str = "Forbidden"):
        self.message = "Forbidden"
        self.description = description
        super().__init__(self.message)
