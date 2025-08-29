from __future__ import annotations

from django.db import models


# M1.2 placeholder: extend in later step to add role field and custom user if needed.
class Placeholder(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        abstract = True
