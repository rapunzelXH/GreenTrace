# greentrace/models/compliance_evidence.py
# UC-08: Upload Photo Evidence  (geotagged photos)
# UC-09: Upload Legal Documents (legal PDF documents)
# FR_22: Geotagged photos | FR_23: Legal docs | FR_43: GPS metadata extraction

from django.db import models

from .user import User
from .eco_milestone import EcoMilestone


class ComplianceEvidence(models.Model):
    """
    Compliance evidence uploaded by a business for a specific milestone.

    Two main categories:
      PHOTO    - Geotagged photo with timestamp (system extracts metadata automatically)
      DOCUMENT - Legal PDF document with expiry date

    After upload -> milestone moves to SUBMITTED status.
    After admin approval (UC-11) -> milestone moves to APPROVED.
    """

    class EvidenceCategory(models.TextChoices):
        PHOTO    = "PHOTO",    "Geotagged Photo"
        DOCUMENT = "DOCUMENT", "Legal Document (PDF)"

    milestone   = models.ForeignKey(
                      EcoMilestone,
                      on_delete=models.CASCADE,
                      related_name="evidence"
                  )
    uploaded_by = models.ForeignKey(
                      User,
                      on_delete=models.PROTECT,
                      related_name="evidence_uploaded"
                  )
    category    = models.CharField(
                      max_length=20,
                      choices=EvidenceCategory.choices
                  )
    file        = models.FileField(
                      upload_to="evidence/%Y/%m/",
                      help_text="Photo (jpg/png) or document (pdf)"
                  )
    description = models.TextField(blank=True)

    # GPS metadata (extracted automatically - FR_43)
    gps_latitude  = models.DecimalField(
                        max_digits=9, decimal_places=6,
                        null=True, blank=True,
                        help_text="Latitude from photo EXIF data"
                    )
    gps_longitude = models.DecimalField(
                        max_digits=9, decimal_places=6,
                        null=True, blank=True,
                        help_text="Longitude from photo EXIF data"
                    )
    captured_at   = models.DateTimeField(
                        null=True, blank=True,
                        help_text="Original timestamp from photo EXIF data"
                    )
    gps_validated = models.BooleanField(
                        default=False,
                        help_text="True if coordinates match the project site location"
                    )

    # For legal documents (UC-09)
    validity_date = models.DateField(
                        null=True, blank=True,
                        help_text="Expiry date of the legal document"
                    )
    document_type = models.CharField(
                        max_length=100, blank=True,
                        help_text="e.g. Waste Permit, Water Test, Transport Permit"
                    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidence [{self.get_category_display()}] for '{self.milestone.title}'"

    class Meta:
        verbose_name        = "Compliance Evidence"
        verbose_name_plural = "Compliance Evidence"
        ordering            = ["-uploaded_at"]
