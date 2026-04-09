from django.urls import path
from users.session_views import RegisterView, LoginView, ProfileView, LogoutView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="session-register"),
    path("login/", LoginView.as_view(), name="session-login"),
    path("profile/", ProfileView.as_view(), name="session-profile"),
    path("logout/", LogoutView.as_view(), name="session-logout"),
]