from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Create an initial superuser if none exists. Supports env vars "
        "DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD."
    )

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS("Superuser already exists; skipping."))
            return

        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin")

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
                "role": User.Role.ADMIN if hasattr(User, "Role") else "admin",
            },
        )
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
        else:
            # Ensure flags set even if user existed but not superuser
            changed = False
            if not user.is_staff:
                user.is_staff = True
                changed = True
            if not user.is_superuser:
                user.is_superuser = True
                changed = True
            if hasattr(user, "role") and user.role != User.Role.ADMIN:
                user.role = User.Role.ADMIN
                changed = True
            if changed:
                user.save()
                self.stdout.write(self.style.WARNING(f"Updated user '{username}' to superuser."))
            else:
                self.stdout.write(self.style.SUCCESS("Superuser present; no changes."))
