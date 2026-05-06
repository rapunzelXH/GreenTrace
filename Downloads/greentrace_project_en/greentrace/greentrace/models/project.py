# greentrace/models/project.py
# FR_30: Admin creates and publishes projects
# FR_36: Admin sets Risk Level (Low / Medium / High)

from django.db import models

from .user import User
from .company_profile import CompanyProfile


class Project(models.Model):
    """
    Environmental procurement project / tender.

    Lifecycle:
        DRAFT -> OPEN -> REVIEW -> EXECUTION -> COMPLETED
                               -> SUSPENDED

    Risk Level displayed with colours on the map (FR_15):
        LOW    -> Green
        MEDIUM -> Orange
        HIGH   -> Red
    """

    class Status(models.TextChoices):
        DRAFT     = "DRAFT",     "Draft"
        OPEN      = "OPEN",      "Open (Accepting Applications)"
        REVIEW    = "REVIEW",    "Under Review"
        EXECUTION = "EXECUTION", "In Execution"
        COMPLETED = "COMPLETED", "Completed"
        SUSPENDED = "SUSPENDED", "Suspended"

    class RiskLevel(models.TextChoices):
        LOW    = "LOW",    "Low    (Green)"
        MEDIUM = "MEDIUM", "Medium (Orange)"
        HIGH   = "HIGH",   "High   (Red)"

    title               = models.CharField(max_length=255)
    description         = models.TextField()
    location            = models.CharField(max_length=255)
    latitude            = models.DecimalField(
                              max_digits=9, decimal_places=6,
                              null=True, blank=True,
                              help_text="GPS coordinate - latitude (FR_11)"
                          )
    longitude           = models.DecimalField(
                              max_digits=9, decimal_places=6,
                              null=True, blank=True,
                              help_text="GPS coordinate - longitude (FR_11)"
                          )
    status              = models.CharField(
                              max_length=20,
                              choices=Status.choices,
                              default=Status.DRAFT
                          )
    risk_level          = models.CharField(
                              max_length=10,
                              choices=RiskLevel.choices,
                              default=RiskLevel.MEDIUM
                          )
    created_by          = models.ForeignKey(
                              User,
                              on_delete=models.PROTECT,
                              related_name="projects_created",
                              limit_choices_to={"role": User.Role.ADMIN}
                          )
    winning_business    = models.ForeignKey(
                              CompanyProfile,
                              on_delete=models.SET_NULL,
                              null=True, blank=True,
                              related_name="won_projects",
                              help_text="Winning business after UC-07"
                          )
    submission_deadline = models.DateTimeField(
                              help_text="Deadline for submitting applications"
                          )
    start_date          = models.DateField(null=True, blank=True)
    end_date            = models.DateField(null=True, blank=True)
    budget              = models.DecimalField(
                              max_digits=15, decimal_places=2,
                              null=True, blank=True
                          )
    has_red_flag        = models.BooleanField(
                              default=False,
                              help_text="True when a journalist submits a discrepancy report (UC-16)"
                          )
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}  [{self.get_status_display()}]"

    class Meta:
        verbose_name        = "Project"
        verbose_name_plural = "Projects"
        ordering            = ["-created_at"]
