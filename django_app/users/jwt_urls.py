from django.urls import path
from users.jwt_views import (
    JWTRegisterView,
    JWTLoginView,
    JWTProfileView,
    JWTRefreshView,
    JWTLogoutView,
)

urlpatterns = [
    path("register/", JWTRegisterView.as_view(), name="jwt-register"),
    path("login/", JWTLoginView.as_view(), name="jwt-login"),
    path("profile/", JWTProfileView.as_view(), name="jwt-profile"),
    path("token/refresh/", JWTRefreshView.as_view(), name="jwt-refresh"),
    path("logout/", JWTLogoutView.as_view(), name="jwt-logout"),
]