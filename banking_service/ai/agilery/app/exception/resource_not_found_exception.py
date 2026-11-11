"""
Resource-not-found exception.
"""


class ResourceNotFoundException(Exception):
    def __init__(self, description: str):
        self.message = "Resource not found"
        self.description = description
        super().__init__(self.message)
