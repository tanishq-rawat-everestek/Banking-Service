import logging
import os
import time
from typing import Optional

import httpx
import jwt
from ai.agilery.app.config.settings import settings
from ai.agilery.app.exception.authentication_exception import AuthenticationException
from ai.agilery.app.exception.authorization_exception import AuthorizationException
from ai.agilery.app.validation.service.security_validation_service import (
    SecurityValidationService,
)
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import (
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidTokenError,
)

logger = logging.getLogger(__name__)

# Required claims for Agilery tokens
REQUIRED_CLAIMS = {"role", "sub"}


def build_rsa_public_key(jwk: dict) -> RSAPublicKey:
    """Build RSA public key from JWK."""
    return jwt.algorithms.RSAAlgorithm.from_jwk(jwk)  # type: ignore


# Reusable HTTP client to avoid resource leaks
_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    """Get or create singleton HTTP client for JWKS fetching."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=3.0)
    return _http_client


async def _fetch_jwks():
    logger.info("Fetching JWKS from %s", settings.JWKS_URL)
    client = get_http_client()
    response = await client.get(settings.JWKS_URL)
    response.raise_for_status()
    return response.json()


def _validate_required_claims(payload: dict):
    """Ensure token contains required claims."""
    missing = REQUIRED_CLAIMS - payload.keys()
    if missing:
        raise AuthorizationException(f"Missing claims: {missing}")


def create_access_token(data: dict, expires_in_minutes: int = 60) -> str:
    """
    Generate a JWT token using settings and PyJWT.
    (Requires a private key or secret to be configured in settings).
    """
    to_encode = data.copy()
    to_encode.update({"exp": int(time.time()) + (expires_in_minutes * 60)})
    to_encode.update({"iss": settings.JWT_ISSUER, "aud": settings.JWT_AUDIENCE})

    # JWT_SECRET must be configured via environment variable
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise ValueError("JWT_SECRET environment variable is not configured")
    return jwt.encode(to_encode, secret, algorithm="HS256")


def get_jwks_keys() -> list[dict]:
    """
    Returns the public keys for JWKS (JSON Web Key Set).
    Used by the Auth Service to expose its public keys.
    """
    return []


def create_refresh_token(data: dict, expires_in_days: int = 7) -> str:
    """
    Generate a JWT refresh token.
    """
    return create_access_token(data, expires_in_minutes=expires_in_days * 24 * 60)


def decode_token(token: str) -> dict:
    """
    Decode token without verification for reading claims,
    or just use validate_jwt_token.
    """
    return jwt.decode(token, options={"verify_signature": False})


async def validate_jwt_token(token: str) -> dict:
    """
    Validates JWT and returns decoded payload.
    Raises AuthenticationException on failure.
    """

    try:
        # Read header
        header = jwt.get_unverified_header(token)

        if header.get("alg") != settings.ALLOWED_JWT_ALGORITHM:
            raise AuthenticationException("Invalid token algorithm")

        kid = header.get("kid")
        if not kid:
            raise AuthenticationException("Missing kid in token")

        # Fetch JWKS
        jwks = await _fetch_jwks()

        jwk = next(
            (key for key in jwks.get("keys", []) if key.get("kid") == kid),
            None,
        )

        if not jwk:
            raise AuthenticationException("No matching JWK found")

        public_key = build_rsa_public_key(jwk)

        # Decode & verify
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[settings.ALLOWED_JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={"require": ["exp", "iat", "sub", "iss", "aud"]},
        )

        # Extra safety
        if payload.get("iat", 0) > int(time.time()):
            raise AuthenticationException("Token issued in the future")

        # Ensure required claims
        _validate_required_claims(payload)

        logger.info("JWT validated for subject: %s", payload.get("sub"))
        return payload

    except ExpiredSignatureError:
        raise AuthenticationException("Token expired")

    except InvalidAudienceError:
        raise AuthenticationException("Invalid audience")

    except InvalidIssuerError:
        raise AuthenticationException("Invalid issuer")

    except InvalidTokenError as exc:
        raise AuthenticationException(f"Invalid token: {exc}")

    except httpx.HTTPError as exc:
        logger.exception("JWKS fetch failed")
        raise AuthenticationException("Unable to verify token") from exc


async def validate_bearer_token(bearer_token: str) -> dict:
    """Extract and validate Bearer token."""
    if not bearer_token:
        raise AuthenticationException("Missing Authorization token")

    if bearer_token.startswith("Bearer "):
        token = bearer_token.split(" ", 1)[1]
    else:
        token = bearer_token

    return await validate_jwt_token(token)


# auto_error=False = if token missing, don't auto throw error
bearer_scheme = HTTPBearer(auto_error=False)

security_validation_service = SecurityValidationService()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict:
    """
    Reads user payload from JWT token.

    TEST MODE:
    Authentication is bypassed only when TESTING_MODE is explicitly set to 'true'.
    This mode should NEVER be enabled in production environments.
    """

    # Bypass authentication ONLY during automated testing with explicit flag
    # Critical security check: ensure this is never accidentally enabled in production
    testing_mode = os.getenv("TESTING_MODE", "false").lower() == "true"
    env = os.getenv("ENV", "production").lower()

    if testing_mode:
        # Additional safety check: block testing mode in production environment
        if env == "production" or env == "prod":
            logger.critical(
                "TESTING_MODE is enabled in production environment - this is a security violation!"
            )
            raise AuthenticationException(
                "Authentication bypass is not allowed in production"
            )
        logger.warning("TESTING_MODE is enabled - authentication is bypassed")
        return {}

    if credentials is None:
        raise AuthenticationException("Missing Authorization token")

    return await validate_bearer_token(credentials.credentials)


def require_permission(permission: str):
    """
    FastAPI dependency for permission validation.

    Example:
        Depends(require_permission("READ_ORDERS"))
    """

    async def _check(user_payload: dict = Depends(get_current_user)):
        testing_mode = os.getenv("TESTING_MODE", "false").lower() == "true"
        env = os.getenv("ENV", "production").lower()

        if testing_mode:
            # Additional safety check: block testing mode in production
            if env == "production" or env == "prod":
                logger.critical(
                    "TESTING_MODE is enabled in production environment - this is a security violation!"
                )
                raise AuthorizationException(
                    "Authorization bypass is not allowed in production"
                )
            return

        security_validation_service.validate_permission(user_payload, permission)

    return _check
