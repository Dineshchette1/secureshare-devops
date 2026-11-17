from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "size_display", "uploaded_at", "expires_at", "download_count")
    list_filter = ("uploaded_at", "expires_at")
    search_fields = ("title", "original_name")
    readonly_fields = ("share_token", "uploaded_at", "download_count", "size_bytes")
