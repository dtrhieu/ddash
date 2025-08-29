from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based permissions."""

    class Role(models.TextChoices):
        VIEWER = "viewer", "Viewer"
        EDITOR = "editor", "Editor"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text="User's role determines their permissions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
