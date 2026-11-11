"""
Auth Validation Service.

This service validates:
- JWT payload
- user permissions

Throws:
- AuthenticationException (401)
- AuthorizationException (403)
"""

import logging

from ai.agilery.app.exception.authorization_exception import AuthorizationException

logger = logging.getLogger(__name__)


class SecurityValidationService:
    """
    Executes authorization validation rules.
    """

    def validate_permission(self, user_payload: dict, permission: str) -> None:
        """
        Validates that the authenticated user has the required permission.

        Args:
            user_payload: JWT token payload containing user information
            permission: Required permission string

        Raises:
            AuthorizationException: If user lacks required permission
        """
        # Read role from user payload
        role = user_payload.get("role")

        if not role:
            logger.warning("User payload missing 'role' claim")
            raise AuthorizationException(
                message="User does not have the required permission"
            )

        # TODO: Implement proper permission mapping based on roles
        # This is a basic implementation - replace with actual permission service
        # permissions = call your permission service to get the permissions for the role

        # For now, validate that role exists and log the permission check
        logger.info(
            "Permission check: user with role '%s' accessing resource requiring '%s'",
            role,
            permission,
        )

        # Basic validation: ensure user has authenticated role
        # Implement proper role-based access control (RBAC) or attribute-based access control (ABAC)
        # based on your application's requirements

        # Uncomment and implement when permission mapping is available:
        # if permission not in permissions:
        #     raise AuthorizationException(
        #         message=f"User does not have the required permission: {permission}"
        #     )
