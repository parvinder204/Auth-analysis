from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from store import user_store

router = APIRouter()


class UserCredentials(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(credentials: UserCredentials):
    if not credentials.username.strip() or not credentials.password.strip():
        raise HTTPException(status_code=400, detail="Username and password are required")

    if user_store.exists(credentials.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = user_store.create_user(credentials.username, credentials.password)

    return {
        "message": "User registered successfully",
        "user_id": user["id"],
        "username": user["username"],
        "auth_method": "session"
    }


@router.post("/login")
def login(credentials: UserCredentials, request: Request):
    if not user_store.verify_password(credentials.username, credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = user_store.get_user(credentials.username)
    request.session["user_id"] = user["id"]
    request.session["username"] = user["username"]

    return {
        "message": "Login successful",
        "username": user["username"],
        "user_id": user["id"],
        "auth_method": "session",
        "session_info": {
            "note": "Session ID stored in httpOnly cookie (session key)",
            "storage": "Server-side (Starlette SessionMiddleware, signed cookie)",
        },
        "how_it_works": {
            "step_1": "Credentials verified against in-memory user store",
            "step_2": "User data written into server-managed session",
            "step_3": "Signed session cookie sent via Set-Cookie header",
            "step_4": "Browser sends cookie on every subsequent request",
            "step_5": "Server reads and validates the session cookie"
        }
    }


@router.get("/profile")
def profile(request: Request):
    username = request.session.get("username")

    if not username:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Not authenticated",
                "hint": "No valid session cookie found in request"
            }
        )

    user = user_store.get_user(username)

    return {
        "message": "Profile retrieved via session",
        "username": user["username"],
        "user_id": user["id"],
        "email": user["email"],
        "auth_method": "session",
        "how_it_works": {
            "step_1": "Browser sent the session cookie automatically",
            "step_2": "SessionMiddleware decoded and validated the signed cookie",
            "step_3": "User identity loaded from session data",
            "step_4": "No token verification — server holds the state"
        }
    }


@router.post("/logout")
def logout(request: Request):
    username = request.session.get("username")

    if not username:
        raise HTTPException(status_code=400, detail="No active session found")

    request.session.clear()

    return {
        "message": "Logged out successfully",
        "username": username,
        "auth_method": "session",
        "how_it_works": {
            "step_1": "Session data cleared from server store",
            "step_2": "Cookie invalidated immediately",
            "step_3": "User is logged out across all tabs instantly",
            "advantage": "Instant revocation is a core strength of session auth"
        }
    }