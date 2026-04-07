from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from store import user_store

router = APIRouter()

SECRET_KEY = "fastapi-jwt-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 1

security = HTTPBearer()

blacklisted_tokens: set[str] = set()


class UserCredentials(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh: str


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["type"] = "access"
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload["type"] = "refresh"
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials

    if token in blacklisted_tokens:
        raise HTTPException(status_code=401, detail="Token has been revoked")

    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Expected an access token")

    username = payload.get("sub")
    user = user_store.get_user(username)

    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists")

    return user


@router.post("/register")
def register(credentials: UserCredentials):
    if not credentials.username.strip() or not credentials.password.strip():
        raise HTTPException(status_code=400, detail="Username and password are required")

    if user_store.exists(credentials.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = user_store.create_user(credentials.username, credentials.password)

    access_token = create_access_token({"sub": user["username"]})
    refresh_token = create_refresh_token({"sub": user["username"]})

    return {
        "message": "User registered successfully",
        "user_id": user["id"],
        "username": user["username"],
        "auth_method": "jwt",
        "tokens": {
            "access": access_token,
            "refresh": refresh_token
        }
    }


@router.post("/login")
def login(credentials: UserCredentials):
    if not user_store.verify_password(credentials.username, credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = user_store.get_user(credentials.username)

    access_token = create_access_token({"sub": user["username"]})
    refresh_token = create_refresh_token({"sub": user["username"]})

    return {
        "message": "Login successful",
        "username": user["username"],
        "user_id": user["id"],
        "auth_method": "jwt",
        "tokens": {
            "access": access_token,
            "refresh": refresh_token
        },
        "how_it_works": {
            "step_1": "Credentials verified against user store",
            "step_2": "Server generates two signed JWTs (no DB write)",
            "step_3": "Access token (30min) + Refresh token (1 day) returned",
            "step_4": "Client stores tokens (localStorage or memory)",
            "step_5": "Client sends access token in Authorization: Bearer header"
        }
    }


@router.get("/profile")
def profile(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Profile retrieved via JWT",
        "username": current_user["username"],
        "user_id": current_user["id"],
        "email": current_user["email"],
        "auth_method": "jwt",
        "how_it_works": {
            "step_1": "Client sent token in Authorization: Bearer header",
            "step_2": "Server decoded and verified the JWT signature",
            "step_3": "User identity extracted from token payload",
            "step_4": "No session lookup — token is self-contained",
            "note": "Stateless verification is the core JWT advantage"
        }
    }


@router.post("/token/refresh")
def refresh_token(body: RefreshRequest):
    payload = decode_token(body.refresh)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Expected a refresh token")

    username = payload.get("sub")
    if not user_store.exists(username):
        raise HTTPException(status_code=401, detail="User no longer exists")

    new_access = create_access_token({"sub": username})

    return {
        "message": "Token refreshed successfully",
        "access": new_access,
        "auth_method": "jwt",
        "how_it_works": {
            "step_1": "Client sent the long-lived refresh token",
            "step_2": "Server verified its signature and type",
            "step_3": "New short-lived access token issued",
            "note": "Refresh tokens allow re-auth without re-login"
        }
    }


@router.post("/logout")
def logout(body: RefreshRequest):
    payload = decode_token(body.refresh)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Expected a refresh token")

    blacklisted_tokens.add(body.refresh)

    return {
        "message": "Logged out (refresh token blacklisted)",
        "auth_method": "jwt",
        "how_it_works": {
            "step_1": "Refresh token added to server-side blacklist",
            "step_2": "Existing access tokens still valid until expiry (30 min)",
            "limitation": "Access tokens cannot be instantly revoked in pure JWT",
            "mitigation": "Short TTL (30 min) limits the exposure window",
            "contrast": "Compare this to session auth — sessions revoke instantly"
        }
    }