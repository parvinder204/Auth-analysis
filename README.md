# Auth Showcase — Session vs JWT

A hands-on experiment comparing session-based and JWT authentication across Django and FastAPI.

## Setup and Running

### Terminal 1 — Django

```bash
cd django_app
chmod +x setup.sh && ./setup.sh
source .venv/bin/activate
python manage.py runserver 8000
```

### Terminal 2 — FastAPI

```bash
cd fastapi_app
chmod +x setup.sh && ./setup.sh
source .venv/bin/activate
uvicorn main:app --reload --port 8001
```

### Frontend

```bash
Open: http://localhost:8000/ (Django)
Open: http://localhost:8001/ (FastAPI)
```

## API Endpoints

### Django (port 8000)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/session/register/` | Register user |
| POST | `/api/session/login/` | Login, creates session |
| GET | `/api/session/profile/` | Profile (session cookie required) |
| POST | `/api/session/logout/` | Logout, destroys session |
| POST | `/api/jwt/register/` | Register, returns tokens |
| POST | `/api/jwt/login/` | Login, returns tokens |
| GET | `/api/jwt/profile/` | Profile (Bearer token required) |
| POST | `/api/jwt/token/refresh/` | Exchange refresh for new access token |
| POST | `/api/jwt/logout/` | Blacklist refresh token |

### FastAPI (port 8001)

Same path structure, same response shape — compare the implementation differences.

## What to Observe

### Session Auth Flow

1. **Register / Login** — notice no token in response body, state lives server-side
2. **Profile** — works automatically because browser sends the session cookie
3. **Logout** — session is deleted from DB, access revoked instantly

### JWT Flow

1. **Login** — access token (30min) and refresh token (1 day) returned in response body
2. **Profile** — requires the Authorization header with Bearer token
3. **Refresh** — exchange refresh token for a new access token without re-login
4. **Logout** — only the refresh token is blacklisted; access token stays valid until expiry

## Key Differences to Note in Responses

Each endpoint response includes a `how_it_works` field explaining exactly what happened internally at that step. Read these as you go through the flows.

### Session
- `session_info.session_key` — the ID stored in the browser cookie
- Logout immediately invalidates access

### JWT
- `tokens.access` — short-lived, stateless
- `tokens.refresh` — long-lived, used to get new access tokens
- Logout only blacklists the refresh token

## Security Notes

These servers are configured for local development only:

- Secret keys are hardcoded — change them in production
- `DEBUG = True` in Django
- FastAPI uses an in-memory user store — data resets on restart
- CORS is wide open (`allow_origins=["*"]`)
- No HTTPS

## Dependencies

**Django**
- `djangorestframework` — REST API layer
- `djangorestframework-simplejwt` — JWT support
- `django-cors-headers` — CORS middleware

**FastAPI**
- `fastapi` + `uvicorn` — server
- `PyJWT` — JWT encode/decode
- `starlette` — session middleware (included with FastAPI)
- `pydantic` — request validation