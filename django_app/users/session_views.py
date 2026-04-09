import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(View):
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

        return JsonResponse({
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username,
            "auth_method": "session"
        }, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        user = authenticate(request, username=username, password=password)

        if user is None:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        login(request, user)

        session_info = {
            "session_key": request.session.session_key,
            "session_expiry": request.session.get_expiry_age(),
        }

        return JsonResponse({
            "message": "Login successful",
            "username": user.username,
            "user_id": user.id,
            "auth_method": "session",
            "session_info": session_info,
            "how_it_works": {
                "step_1": "Credentials verified against database",
                "step_2": "Django creates a session entry in the database",
                "step_3": "Session ID is sent to client via Set-Cookie header",
                "step_4": "Browser stores session ID in cookie (httpOnly)",
                "step_5": "Every subsequent request sends the cookie automatically"
            }
        })


@method_decorator(csrf_exempt, name="dispatch")
class ProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({
                "error": "Not authenticated",
                "hint": "No valid session cookie found"
            }, status=401)

        return JsonResponse({
            "message": "Profile retrieved via session",
            "username": request.user.username,
            "user_id": request.user.id,
            "email": request.user.email,
            "auth_method": "session",
            "session_key": request.session.session_key,
            "how_it_works": {
                "step_1": "Browser sent session ID cookie automatically",
                "step_2": "SessionMiddleware fetched session from database",
                "step_3": "AuthenticationMiddleware attached user to request",
                "step_4": "No token validation needed — server owns the state"
            }
        })


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Not logged in"}, status=400)

        username = request.user.username
        session_key = request.session.session_key
        logout(request)

        return JsonResponse({
            "message": "Logged out successfully",
            "username": username,
            "auth_method": "session",
            "how_it_works": {
                "step_1": f"Session {session_key} deleted from database",
                "step_2": "Cookie cleared from browser",
                "step_3": "Token is immediately invalid — no grace period",
                "advantage": "Instant revocation is a key strength of session auth"
            }
        })