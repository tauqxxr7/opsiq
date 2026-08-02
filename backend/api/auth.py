from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from core.security import ALL_ROLES, Role, current_user, decode_token, issue_tokens, require_roles, verify_password

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


@router.post("/login")
async def login(payload: LoginRequest, request: Request):
    user = request.app.state.store.get_user(payload.username, include_hash=True)
    if not user or not user["active"] or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return issue_tokens(user)


@router.post("/refresh")
async def refresh(payload: RefreshRequest, request: Request):
    claims = decode_token(payload.refresh_token, "refresh")
    user = request.app.state.store.get_user(claims["sub"])
    if not user or not user["active"]:
        raise HTTPException(status_code=401, detail="User is unavailable")
    return issue_tokens(user)


@router.get("/me")
async def me(user: dict = Depends(current_user)):
    return {key: user[key] for key in ("username", "display_name", "role")}


@router.get("/roles")
async def roles(user: dict = Depends(current_user)):
    return {"roles": sorted(ALL_ROLES), "current_role": user["role"]}


@router.get("/users")
async def users(request: Request, _: dict = Depends(require_roles(Role.ADMINISTRATOR))):
    return {"users": request.app.state.store.list_users()}


@router.post("/users", status_code=201)
async def create_user(payload: UserCreate, request: Request, _: dict = Depends(require_roles(Role.ADMINISTRATOR))):
    if payload.role not in ALL_ROLES:
        raise HTTPException(status_code=422, detail="Unsupported role")
    if request.app.state.store.get_user(payload.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    return request.app.state.store.create_user(payload.model_dump())

