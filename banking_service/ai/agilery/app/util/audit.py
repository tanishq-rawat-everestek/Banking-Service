"""
Helpers for applying common audit fields.
"""


def apply_created_audit(entity, user: dict | None) -> None:
    if isinstance(user, dict) and hasattr(entity, "created_by"):
        entity.created_by = (
            user.get("email")
            or user.get("preferred_username")
            or user.get("name")
            or user.get("sub")
        )


def apply_modified_audit(entity, user: dict | None) -> None:
    if isinstance(user, dict) and hasattr(entity, "modified_by"):
        entity.modified_by = (
            user.get("email")
            or user.get("preferred_username")
            or user.get("name")
            or user.get("sub")
        )
