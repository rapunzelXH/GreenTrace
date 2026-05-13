# greentrace/models/tender_application.py
# UC-06: Apply for Green Tender
# UC-07: Review Business Bids
# FR_21: Businesses apply for open tenders
# FR_28: Save draft application

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .user import User
from .project import Project
from .company_profile import CompanyProfile


class TenderApplication(models.Model):
    """
    A business application for an open tender.

    Each (project, business) pair can have only one application (unique_together).

    Status flow:
        DRAFT  ->  SUBMITTED  ->  SHORTLISTED  ->  APPROVED  (winner)
                              ->  REJECTED                    (from UC-07)
    """

    class AppStatus(models.TextChoices):
        DRAFT       = "DRAFT",       "Draft"
        SUBMITTED   = "SUBMITTED",   "Submitted"
        SHORTLISTED = "SHORTLISTED", "Shortlisted"
        APPROVED    = "APPROVED",    "Approved / Winner"
        REJECTED    = "REJECTED",    "Rejected"

    project              = models.ForeignKey(
                               Project,
                               on_delete=models.CASCADE,
                               related_name="applications"
                           )
    business             = models.ForeignKey(
                               CompanyProfile,
                               on_delete=models.CASCADE,
                               related_name="applications"
                           )
    status               = models.CharField(
                               max_length=20,
                               choices=AppStatus.choices,
                               default=AppStatus.DRAFT
                           )
    technical_proposal   = models.FileField(
                               upload_to="applications/technical/",
                               help_text="Business technical proposal (PDF)"
                           )
    env_impact_statement = models.FileField(
                               upload_to="applications/env_impact/",
                               help_text="Environmental Impact Statement (PDF)"
                           )
    financial_bid        = models.DecimalField(
                               max_digits=15, decimal_places=2,
                               help_text="Financial bid amount"
                           )
    admin_score          = models.FloatField(
                               null=True, blank=True,
                               validators=[MinValueValidator(0), MaxValueValidator(100)],
                               help_text="Score assigned by admin after UC-07"
                           )
    rejection_reason     = models.TextField(
                               blank=True,
                               help_text="Reason for rejection by admin"
                           )
    submitted_at         = models.DateTimeField(
                               null=True, blank=True,
                               help_text="Timestamp of final submission"
                           )
    evaluated_by         = models.ForeignKey(
                               User,
                               on_delete=models.SET_NULL,
                               null=True, blank=True,
                               related_name="evaluated_applications",
                               limit_choices_to={"role": User.Role.ADMIN}
                           )
    created_at           = models.DateTimeField(auto_now_add=True)
    updated_at           = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.business.company_name}  ->  "
            f"{self.project.title}  [{self.get_status_display()}]"
        )

    class Meta:
        verbose_name        = "Tender Application"
        verbose_name_plural = "Tender Applications"
        unique_together     = ("project", "business")
