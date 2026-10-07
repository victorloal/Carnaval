"""Role definitions for `roles-permisos.md` §3.

The public submission tables do not exist until v3; their permissions resolve to
none today and will appear once the models do.
"""

from __future__ import annotations

from django.contrib.auth.models import Permission

CONTENT_MODELS: dict[str, list[str]] = {
    "programme": ["edition", "day", "venue", "event"],
}
PUBLIC_SUBMISSION_MODELS: dict[str, list[str]] = {
    "submissions": ["submission", "submissionfile", "consentrecord"],
}
INGESTION_META_MODELS: dict[str, list[str]] = {
    "ingestion": ["scrapesource", "ingestionrun"],
}
RAW_PAYLOAD_MODELS: dict[str, list[str]] = {
    "ingestion": ["rawdocument"],
}

_MODERATION_VERBS = ["publish", "reject", "unpublish", "request_changes"]


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
    moderation = _permissions(content, _MODERATION_VERBS)
    view_ingestion_meta = _permissions(INGESTION_META_MODELS, ["view"])
    view_raw = _permissions(RAW_PAYLOAD_MODELS, ["view"])
    return {
        # viewer: read-only, no moderation verb, and no raw third-party payload
        # (matrix rows 4–7 and 11 are a hard deny).
        "viewer": view_content | view_ingestion_meta,
        # editor: adjudicates content and may read the payload to verify it.
        "editor": edit_content | moderation | view_ingestion_meta | view_raw,
        # admin: everything the project defines.
        "admin": set(Permission.objects.all()),
    }
