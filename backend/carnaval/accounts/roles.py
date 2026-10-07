"""Role definitions for `roles-permisos.md` §3.

The matrix has 35 capabilities; this module maps the model-level ones onto
Django permissions. The moderation verbs (`publish_*`, `reject_*`, …) are custom
permissions and land with the review queue in Sprint 09.
"""

from __future__ import annotations

from django.contrib.auth.models import Permission

CONTENT_MODELS: dict[str, list[str]] = {
    "programme": ["edition", "day", "venue", "event"],
}
INGESTION_MODELS: dict[str, list[str]] = {
    "ingestion": ["scrapesource", "rawdocument", "ingestionrun"],
}
PUBLIC_SUBMISSION_MODELS: dict[str, list[str]] = {
    "submissions": ["submission", "submissionfile", "consentrecord"],
}


def _permissions(
    app_models: dict[str, list[str]], actions: list[str]
) -> set[Permission]:
    found: set[Permission] = set()
    for app_label, models in app_models.items():
        for model in models:
            codenames = [f"{action}_{model}" for action in actions]
            found.update(
                Permission.objects.filter(
                    content_type__app_label=app_label, codename__in=codenames
                )
            )
    return found


def role_permissions() -> dict[str, set[Permission]]:
    content = CONTENT_MODELS | PUBLIC_SUBMISSION_MODELS
    view_content = _permissions(content, ["view"])
    edit_content = _permissions(content, ["view", "add", "change"])
    view_ingestion = _permissions(INGESTION_MODELS, ["view"])
    return {
        # viewer: read-only, and never a moderation verb (FR-D-05).
        "viewer": view_content | view_ingestion,
        # editor: moderate and edit content, nothing that changes behaviour.
        "editor": edit_content | view_ingestion,
        # admin: everything the project defines.
        "admin": set(Permission.objects.all()),
    }
