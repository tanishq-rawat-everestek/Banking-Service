"""
Validator ensuring a string is either null or non-blank.
"""


def null_or_not_empty(value: str | None) -> bool:
    if value is None:
        return True
    return value.strip() != ""
