from __future__ import annotations

from django.urls import path

from carnaval.accounts import views

urlpatterns = [
    path("step-up/", views.step_up, name="step-up"),
]
