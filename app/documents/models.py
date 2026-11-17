import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone


def default_expiry():
    """Share links last 7 days unless set otherwise."""
    return timezone.now() + timedelta(days=7)


class Document(models.Model):
    """An uploaded file that can be shared through an unguessable link."""

    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="uploads/%Y/%m/%d/")
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100, blank=True)
    size_bytes = models.PositiveIntegerField(default=0)

    # The share token is the security boundary: a random UUID is far too
    # large to guess, so the link itself grants access.
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)
    download_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [models.Index(fields=["expires_at"])]

    def __str__(self) -> str:
        return self.title

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def size_display(self) -> str:
        size = float(self.size_bytes)
        for unit in ("B", "KB", "MB"):
            if size < 1024:
                return f"{size:.0f} {unit}"
            size /= 1024
        return f"{size:.1f} GB"
