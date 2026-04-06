"""Inbound Entra bearer token verification for the MCP endpoint."""

from __future__ import annotations

import logging

import jwt
from jwt import PyJWKClient
from mcp.server.auth.provider import AccessToken, TokenVerifier

logger = logging.getLogger(__name__)


class EntraTokenVerifier(TokenVerifier):
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        required_scopes: list[str] | None = None,
    ) -> None:
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._required_scopes = set(required_scopes) if required_scopes else set()
        self._allowed_issuers = {
            f"https://login.microsoftonline.com/{tenant_id}/v2.0",
            f"https://sts.windows.net/{tenant_id}/",
        }
        self._allowed_audiences = {
            client_id,
            f"api://{client_id}",
        }
        jwks_url = (
            f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        )
        self._jwks_client = PyJWKClient(jwks_url, cache_keys=True)

    def _normalize_scope_values(self, values: list[str]) -> set[str]:
        normalized: set[str] = set()
        for value in values:
            normalized.add(value)
            if value.startswith("api://") and "/" in value[6:]:
                normalized.add(value.rsplit("/", 1)[-1])
        return normalized

    def _extract_token_scopes(self, payload: dict[str, object]) -> list[str]:
        if "scp" in payload and isinstance(payload["scp"], str):
            return payload["scp"].split()
        if "roles" in payload:
            roles = payload["roles"]
            if isinstance(roles, list):
                return [str(role) for role in roles]
            return [str(roles)]
        return []

    def _has_valid_issuer(self, payload: dict[str, object]) -> bool:
        issuer = payload.get("iss")
        return isinstance(issuer, str) and issuer in self._allowed_issuers

    def _has_valid_audience(self, payload: dict[str, object]) -> bool:
        audience = payload.get("aud")
        if isinstance(audience, str):
            return audience in self._allowed_audiences
        if isinstance(audience, list):
            return any(isinstance(aud, str) and aud in self._allowed_audiences for aud in audience)
        return False

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={
                    "require": ["exp", "iss", "aud"],
                    "verify_aud": False,
                    "verify_iss": False,
                },
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Token verification failed: token expired")
            return None
        except jwt.InvalidTokenError as exc:
            logger.warning("Token verification failed: %s", type(exc).__name__)
            return None

        if not self._has_valid_issuer(payload):
            logger.warning("Token verification failed: invalid issuer")
            return None

        if not self._has_valid_audience(payload):
            logger.warning("Token verification failed: invalid audience")
            return None

        # Extract scopes from Entra tokens: "scp" claim (delegated) or "roles" (app)
        token_scopes = self._extract_token_scopes(payload)
        normalized_required_scopes = self._normalize_scope_values(
            list(self._required_scopes)
        )
        normalized_token_scopes = self._normalize_scope_values(token_scopes)
        effective_scopes = sorted(set(token_scopes))

        if self._required_scopes:
            has_required_scopes = normalized_required_scopes.issubset(normalized_token_scopes)
            allow_app_only_fallback = (
                not token_scopes
                and bool(payload.get("appid") or payload.get("azp"))
            )
            if not has_required_scopes and not allow_app_only_fallback:
                logger.warning("Token missing required scopes")
                return None
            if allow_app_only_fallback:
                logger.info(
                    "Token contains no scp/roles claims; allowing app-only token "
                    "based on issuer and audience validation"
                )
            effective_scopes = sorted(set(effective_scopes) | self._required_scopes)

        return AccessToken(
            token=token,
            client_id=payload.get("azp", payload.get("appid", "")),
            scopes=effective_scopes,
            expires_at=payload.get("exp"),
        )
