from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.http import HttpRequest

from carnaval.audit import services as audit
from carnaval.audit.models import ActorKind
from carnaval.editorial.models import MediaAsset, NewsItem, SiteSetting, Source
from carnaval.moderation.admin import ModeratedAdmin


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "is_official", "url")
    list_filter = ("kind", "is_official")
    search_fields = ("name",)


@admin.register(NewsItem)
class NewsItemAdmin(ModeratedAdmin):
    list_display = ("headline", "outlet", "published_on", "status", "origin")
    search_fields = ("headline", "url", "outlet")


@admin.register(MediaAsset)
class MediaAssetAdmin(ModeratedAdmin):
    list_display = (
        "title_es",
        "year_approx",
        "rights_status",
        "exif_stripped",
        "minor_subject",
        "status",
    )
    list_filter = (
        "status",
        "origin",
        "rights_status",
        "exif_stripped",
        "minor_subject",
        "featured",
    )
    search_fields = ("title_es", "author", "source_ref")
    readonly_fields = ("staged_changes", "reviewed_by", "reviewed_at")


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "value_type", "value", "updated_by", "updated_at")
    search_fields = ("key",)

    def save_model(
        self, request: HttpRequest, obj: Any, form: Any, change: bool
    ) -> None:
        before: Any = None
        if change:
            previous = SiteSetting.objects.filter(pk=obj.pk).first()
            if previous is not None:
                before = previous.value
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
        audit.record(
            action="update",
            actor=request.user if getattr(request.user, "pk", None) else None,
            actor_kind=ActorKind.HUMAN,
            object_type="editorial.sitesetting",
            changes={"before": before, "after": obj.value},
            request=request,
        )
