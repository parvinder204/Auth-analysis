from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles   
from fastapi.responses import RedirectResponse  
from starlette.middleware.sessions import SessionMiddleware


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



@app.get("/health")
def health():
    return {"status": "ok", "service": "FastAPI Auth Showcase"}