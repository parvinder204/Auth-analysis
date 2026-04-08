import json
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def decode_bearer_token(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, "Authorization header missing or malformed"

    token_str = auth_header.split(" ")[1]
    authenticator = JWTAuthentication()

    try:
        validated_token = authenticator.get_validated_token(token_str)
        user = authenticator.get_user(validated_token)
        return user, None
    except (InvalidToken, TokenError) as e:
        return None, str(e)


@method_decorator(csrf_exempt, name="dispatch")
class JWTRegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not username or not password:
            return JsonResponse({"error": "Username and password are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already taken"}, status=400)

        user = User.objects.create_user(username=username, password=password)
        tokens = get_tokens_for_user(user)

        return JsonResponse({
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username,
            "auth_method": "jwt",
            "tokens": tokens,
            "how_it_works": {
                "note": "Tokens issued immediately on registration"
            }
        }, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class JWTLoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        if not user.check_password(password):
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        tokens = get_tokens_for_user(user)

        return JsonResponse({
            "message": "Login successful",
            "username": user.username,
            "user_id": user.id,
            "auth_method": "jwt",
            "tokens": tokens,
            "how_it_works": {
                "step_1": "Credentials verified against database",
                "step_2": "Server generates a signed JWT (no DB write needed)",
                "step_3": "Access token (30min) + Refresh token (1 day) returned",
                "step_4": "Client stores token (localStorage or memory)",
                "step_5": "Client sends token in Authorization: Bearer <token> header"
            }
        })


@method_decorator(csrf_exempt, name="dispatch")
class JWTProfileView(View):
    def get(self, request):
        user, error = decode_bearer_token(request)

        if error:
            return JsonResponse({
                "error": "Not authenticated",
                "detail": error,
                "hint": "Send Authorization: Bearer <access_token> header"
            }, status=401)

        return JsonResponse({
            "message": "Profile retrieved via JWT",
            "username": user.username,
            "user_id": user.id,
            "email": user.email,
            "auth_method": "jwt",
            "how_it_works": {
                "step_1": "Client sent token in Authorization header",
                "step_2": "Server decoded and verified the JWT signature",
                "step_3": "User identity extracted from token payload",
                "step_4": "No database lookup needed — token is self-contained",
                "note": "This is the key advantage: stateless verification"
            }
        })


@method_decorator(csrf_exempt, name="dispatch")
class JWTRefreshView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        refresh_token_str = data.get("refresh")

        if not refresh_token_str:
            return JsonResponse({"error": "Refresh token required"}, status=400)

        try:
            refresh = RefreshToken(refresh_token_str)
            new_access = str(refresh.access_token)

            return JsonResponse({
                "message": "Token refreshed successfully",
                "access": new_access,
                "auth_method": "jwt",
                "how_it_works": {
                    "step_1": "Client sent the long-lived refresh token",
                    "step_2": "Server verified its signature",
                    "step_3": "New short-lived access token issued",
                    "note": "Refresh tokens allow seamless re-auth without re-login"
                }
            })
        except TokenError as e:
            return JsonResponse({"error": "Invalid refresh token", "detail": str(e)}, status=401)


@method_decorator(csrf_exempt, name="dispatch")
class JWTLogoutView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        refresh_token_str = data.get("refresh")

        if not refresh_token_str:
            return JsonResponse({"error": "Refresh token required to logout"}, status=400)

        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()

            return JsonResponse({
                "message": "Logged out (refresh token blacklisted)",
                "auth_method": "jwt",
                "how_it_works": {
                    "step_1": "Refresh token added to blacklist table",
                    "step_2": "Existing access tokens still valid until expiry",
                    "limitation": "Access token cannot be instantly revoked in stateless JWT",
                    "mitigation": "Short access token TTL (30 min) limits the risk window"
                }
            })
        except TokenError as e:
            return JsonResponse({"error": "Invalid token", "detail": str(e)}, status=400)