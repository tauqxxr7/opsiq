import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from enum import Enum

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class Role(str, Enum):
    OPERATOR = "Operator"
    MAINTENANCE_ENGINEER = "Maintenance Engineer"
    RELIABILITY_ENGINEER = "Reliability Engineer"
    SAFETY_ENGINEER = "Safety Engineer"
    SUPERVISOR = "Supervisor"
    PLANT_MANAGER = "Plant Manager"
    ADMINISTRATOR = "Administrator"
    AUDITOR = "Auditor"


ALL_ROLES = {role.value for role in Role}
AUTH_REQUIRED = os.getenv("OPSIQ_AUTH_REQUIRED", "false").lower() == "true"
JWT_SECRET = os.getenv("OPSIQ_JWT_SECRET", "")
ACCESS_TTL_SECONDS = int(os.getenv("OPSIQ_ACCESS_TOKEN_MINUTES", "15")) * 60
REFRESH_TTL_SECONDS = int(os.getenv("OPSIQ_REFRESH_TOKEN_DAYS", "7")) * 86400
bearer = HTTPBearer(auto_error=False)

if AUTH_REQUIRED and (len(JWT_SECRET) < 32 or JWT_SECRET.startswith("replace_")):
    raise RuntimeError("OPSIQ_JWT_SECRET must be a non-placeholder secret of at least 32 characters when authentication is enabled")


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt$16384$8$1${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        _, n, r, p, salt, expected = encoded.split("$")
        digest = hashlib.scrypt(password.encode(), salt=base64.urlsafe_b64decode(salt), n=int(n), r=int(r), p=int(p))
        return hmac.compare_digest(base64.urlsafe_b64encode(digest).decode(), expected)
    except (ValueError, TypeError):
        return False


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_token(subject: str, role: str, token_type: str, ttl: int, jti: str | None = None) -> str:
    if not JWT_SECRET:
        raise RuntimeError("OPSIQ_JWT_SECRET is required to issue tokens")
    now = int(time.time())
    payload = {"sub": subject, "role": role, "type": token_type, "iat": now, "exp": now + ttl, "jti": jti or secrets.token_urlsafe(12)}
    header = {"alg": "HS256", "typ": "JWT"}
    unsigned = f"{_b64(json.dumps(header, separators=(',', ':')).encode())}.{_b64(json.dumps(payload, separators=(',', ':')).encode())}"
    signature = _b64(hmac.new(JWT_SECRET.encode(), unsigned.encode(), hashlib.sha256).digest())
    return f"{unsigned}.{signature}"


def decode_token(token: str, expected_type: str) -> dict:
    if not JWT_SECRET:
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    try:
        header, payload, signature = token.split(".")
        unsigned = f"{header}.{payload}"
        expected = _b64(hmac.new(JWT_SECRET.encode(), unsigned.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("signature")
        data = json.loads(_decode(payload))
        if not data.get("sub") or not data.get("jti") or data.get("type") != expected_type or int(data.get("exp", 0)) <= int(time.time()):
            raise ValueError("expired or wrong token type")
        return data
    except (ValueError, TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from None


def issue_tokens(user: dict, store, refresh_jti: str | None = None, persist_refresh: bool = True) -> dict:
    refresh_jti = refresh_jti or secrets.token_urlsafe(24)
    refresh_expires_at = int(time.time()) + REFRESH_TTL_SECONDS
    access_token = create_token(user["username"], user["role"], "access", ACCESS_TTL_SECONDS)
    refresh_token = create_token(user["username"], user["role"], "refresh", REFRESH_TTL_SECONDS, refresh_jti)
    if persist_refresh:
        store.create_refresh_session(user["username"], refresh_jti, refresh_expires_at)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TTL_SECONDS,
        "user": {key: user[key] for key in ("username", "display_name", "role")},
    }


async def current_user(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if not AUTH_REQUIRED and credentials is None:
        return {"username": "system", "display_name": "Local development", "role": Role.ADMINISTRATOR.value}
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    claims = decode_token(credentials.credentials, "access")
    user = request.app.state.store.get_user(claims["sub"])
    if not user or not user["active"]:
        raise HTTPException(status_code=401, detail="User is unavailable")
    return user


def require_roles(*roles: Role):
    allowed = {role.value for role in roles}
    async def dependency(user: dict = Depends(current_user)) -> dict:
        if user["role"] not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient role permission")
        return user
    return dependency
