import secrets
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from core.permissions import Permission, authorize
from core.security import ALL_ROLES, REFRESH_TTL_SECONDS, decode_token, issue_tokens, verify_password

router = APIRouter()


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=8, max_length=256)


class RefreshRequest(BaseModel):
    refresh_token: str


class UserCreate(BaseModel):
    username: str = Field(pattern=r"^[A-Za-z0-9._-]{3,80}$")
    display_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=12, max_length=256)
    role: str


class UserUpdate(BaseModel):
    role: str | None = None
    active: bool | None = None


@router.post("/login")
async def login(payload: LoginRequest, request: Request):
    store = request.app.state.store
    user = store.get_user(payload.username, include_hash=True)
    if not user or not user["active"] or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return issue_tokens(user, store)


@router.post("/refresh")
async def refresh(payload: RefreshRequest, request: Request):
    claims = decode_token(payload.refresh_token, "refresh")
    store = request.app.state.store
    user = store.get_user(claims["sub"])
    if not user or not user["active"]:
        raise HTTPException(status_code=401, detail="User is unavailable")
    new_jti = secrets.token_urlsafe(24)
    if not store.rotate_refresh_session(user["username"], claims["jti"], new_jti, int(time.time()) + REFRESH_TTL_SECONDS):
        raise HTTPException(status_code=401, detail="Refresh session is revoked or unavailable")
    return issue_tokens(user, store, refresh_jti=new_jti, persist_refresh=False)


@router.post("/logout")
async def logout(payload: RefreshRequest, request: Request):
    claims = decode_token(payload.refresh_token, "refresh")
    request.app.state.store.revoke_refresh_session(claims["sub"], claims["jti"])
    return {"status": "logged_out"}


@router.get("/me")
async def me(user: dict = Depends(authorize(Permission.GENERAL_READ))):
    return {key: user[key] for key in ("username", "display_name", "role")}


@router.get("/roles")
async def roles(user: dict = Depends(authorize(Permission.GENERAL_READ))):
    return {"roles": sorted(ALL_ROLES), "current_role": user["role"]}


@router.get("/users")
async def users(request: Request, _: dict = Depends(authorize(Permission.USER_ADMIN))):
    return {"users": request.app.state.store.list_users()}


@router.post("/users", status_code=201)
async def create_user(payload: UserCreate, request: Request, _: dict = Depends(authorize(Permission.USER_ADMIN))):
    if payload.role not in ALL_ROLES:
        raise HTTPException(status_code=422, detail="Unsupported role")
    if request.app.state.store.get_user(payload.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    return request.app.state.store.create_user(payload.model_dump())


@router.patch("/users/{username}")
async def update_user(username: str, payload: UserUpdate, request: Request, _: dict = Depends(authorize(Permission.USER_ADMIN))):
    if payload.role is not None and payload.role not in ALL_ROLES:
        raise HTTPException(status_code=422, detail="Unsupported role")
    user = request.app.state.store.update_user(username, payload.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users/{username}/revoke-sessions")
async def revoke_user_sessions(username: str, request: Request, _: dict = Depends(authorize(Permission.USER_ADMIN))):
    if not request.app.state.store.get_user(username):
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "revoked", "sessions_revoked": request.app.state.store.revoke_all_sessions(username)}
