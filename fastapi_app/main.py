from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles   
from fastapi.responses import RedirectResponse  
from starlette.middleware.sessions import SessionMiddleware

from routers import session_router, jwt_router

app = FastAPI(
    title="Auth Showcase - FastAPI",
    description="Demonstrates session and JWT authentication patterns",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],          # add e.g. "http://localhost:5173" if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="fastapi-session-secret-key-change-in-production",
    max_age=3600,
    same_site="lax",
    https_only=False,
)

app.include_router(session_router.router, prefix="/api/session", tags=["Session Auth"])
app.include_router(jwt_router.router,     prefix="/api/jwt",     tags=["JWT Auth"])

# Requires: pip install aiofiles
app.mount("/static", StaticFiles(directory="../frontend"), name="static")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/health")
def health():
    return {"status": "ok", "service": "FastAPI Auth Showcase"}