# greentrace/models/company_profile.py
# FR_20: Businesses create a profile and upload certificates (ISO 14001, QKB)

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .user import User


class CompanyProfile(models.Model):
    """
    Company profile for Business users.
    Each Business user has exactly one CompanyProfile (OneToOne).
    Used for tender applications and Eco-Score calculation.
    """

    user            = models.OneToOneField(
                          User,
                          on_delete=models.CASCADE,
                          related_name="company_profile",
                          limit_choices_to={"role": User.Role.BUSINESS},
                          help_text="The Business user linked to this profile"
                      )
    company_name    = models.CharField(max_length=255)
    registration_no = models.CharField(
                          max_length=100,
                          unique=True,
                          help_text="Business registration number (NIPT)"
                      )
    address         = models.TextField()
    phone           = models.CharField(max_length=20)
    website         = models.URLField(blank=True)
    iso_certificate = models.FileField(
                          upload_to="certificates/iso/",
                          blank=True,
                          help_text="ISO 14001 or other environmental certificate"
                      )
    qkb_document    = models.FileField(
                          upload_to="certificates/qkb/",
                          blank=True,
                          help_text="QKB document (National Business Centre)"
                      )
    eco_score       = models.FloatField(
                          default=0.0,
                          validators=[MinValueValidator(0), MaxValueValidator(100)],
                          help_text="Environmental score 0-100, calculated automatically (FR_41)"
                      )
    is_verified     = models.BooleanField(
                          default=False,
                          help_text="Profile verified by admin"
                      )
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name}  (Eco-Score: {self.eco_score})"

    class Meta:
        verbose_name        = "Company Profile"
        verbose_name_plural = "Company Profiles"
