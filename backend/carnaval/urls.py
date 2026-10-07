"""
URL configuration for carnaval project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

from carnaval.api.health import health
from carnaval.ingestion.views import raw_payload
from carnaval.legal.views import takedown
from carnaval.submissions.views import submission_status, submit

urlpatterns = [
    # Before the admin include so the custom payload route wins.
    path("admin/raw-payload/<uuid:pk>/", raw_payload, name="raw-payload"),
    path("admin/", admin.site.urls),
    path("accounts/", include("carnaval.accounts.urls")),
    path("api/submissions/", submit, name="submission-submit"),
    path(
        "api/submissions/<str:token>/",
        submission_status,
        name="submission-status",
    ),
    path("api/", include("carnaval.api.urls")),
    path("takedown/", takedown, name="takedown"),
    path("health", health),
    path("health/", health),
]
