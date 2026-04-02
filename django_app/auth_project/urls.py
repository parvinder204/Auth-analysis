from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/session/", include("users.session_urls")),
    path("api/jwt/", include("users.jwt_urls")),
    path("", TemplateView.as_view(template_name="index.html")),
]