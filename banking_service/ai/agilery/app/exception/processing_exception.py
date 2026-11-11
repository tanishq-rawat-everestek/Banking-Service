"""
Processing exception.
"""


class ProcessingException(Exception):
    def __init__(self, message: str = "Internal Server Error"):
        self.message = message
        super().__init__(self.message)
