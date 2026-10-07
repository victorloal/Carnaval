"""
URL configuration for carnaval project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

from carnaval.api.health import health
from carnaval.ingestion.views import raw_payload

urlpatterns = [
    # Before the admin include so the custom payload route wins.
    path("admin/raw-payload/<uuid:pk>/", raw_payload, name="raw-payload"),
    path("admin/", admin.site.urls),
    path("accounts/", include("carnaval.accounts.urls")),
    path("api/", include("carnaval.api.urls")),
    path("health", health),
    path("health/", health),
]
