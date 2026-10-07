from __future__ import annotations

from django.contrib import admin

from carnaval.moderation.admin import ModeratedAdmin
from carnaval.submissions.models import ConsentRecord, Submission, SubmissionFile


class SubmissionFileInline(admin.TabularInline):
    model = SubmissionFile
    extra = 0
    readonly_fields = (
        "quarantine_key",
        "mime_detected",
        "declared_mime",
        "content_hash",
        "byte_size",
        "width",
        "height",
        "exif_stripped",
    )
    can_delete = False


class ConsentRecordInline(admin.TabularInline):
    model = ConsentRecord
    extra = 0
    readonly_fields = (
        "legal_document",
        "accepted_at",
        "ip_hash",
        "declaration_rights",
        "declaration_minor_subject",
    )
    can_delete = False


@admin.register(Submission)
class SubmissionAdmin(ModeratedAdmin):
    list_display = ("public_token", "kind", "status", "origin", "declared_author")
    inlines = [SubmissionFileInline, ConsentRecordInline]
    readonly_fields = ("public_token", "staged_changes", "reviewed_by", "reviewed_at")
