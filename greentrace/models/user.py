# greentrace/models/user.py
# FR_01-FR_09: Role-based access, login, registration, audit

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    GreenTrace system user with three roles:
      - ADMIN      : Government Administrator (The Regulator)
      - BUSINESS   : Contractor / Company     (The Contractor)
      - JOURNALIST : Journalist / Public User  (The Watchdog)

    Extends AbstractUser -> includes username, email, password, is_active etc.
    """

    class Role(models.TextChoices):
        ADMIN      = "ADMIN",      "Government Administrator"
        BUSINESS   = "BUSINESS",   "Business / Contractor"
        JOURNALIST = "JOURNALIST", "Journalist / Public"

    role               = models.CharField(
                             max_length=20,
                             choices=Role.choices,
                             help_text="User role in the system"
                         )
    is_email_verified  = models.BooleanField(
                             default=False,
                             help_text="Email confirmed (FR_08)"
                         )
    is_suspended       = models.BooleanField(
                             default=False,
                             help_text="Account suspended by admin (FR_35)"
                         )
    failed_login_count = models.PositiveSmallIntegerField(
                             default=0,
                             help_text="Number of failed login attempts (FR_09)"
                         )
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name        = "User"
        verbose_name_plural = "Users"
