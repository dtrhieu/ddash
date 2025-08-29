from __future__ import annotations

from django.db import models


# M1.2 placeholder: domain models to be added per spec in later steps.
class Placeholder(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        abstract = True
