# greentrace/models/discrepancy_report.py
# UC-16: Report Discrepancy (Whistleblowing)
# FR_17: Anonymous form with file upload (photo/video)
# FR_37: Admin receives and responds to reports

from django.db import models

from .user import User
from .project import Project


class DiscrepancyReport(models.Model):
    """
    Violation report submitted by a journalist or public user.

    The reporter can choose:
      - Anonymous   -> reported_by = NULL, is_anonymous = True
      - Verified    -> reported_by = User (Journalist)

    When the report is accepted, the system sets has_red_flag = True
    on the related project and notifies the admin (FR_37).
    """

    class ReportStatus(models.TextChoices):
        PENDING      = "PENDING",      "Pending Review"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        RESOLVED     = "RESOLVED",     "Resolved"
        DISMISSED    = "DISMISSED",    "Dismissed"

    project        = models.ForeignKey(
                         Project,
                         on_delete=models.CASCADE,
                         related_name="discrepancy_reports"
                     )
    reported_by    = models.ForeignKey(
                         User,
                         on_delete=models.SET_NULL,
                         null=True, blank=True,
                         related_name="reports_submitted",
                         help_text="NULL when the report is anonymous (is_anonymous=True)"
                     )
    is_anonymous   = models.BooleanField(
                         default=False,
                         help_text="If True, the reporter's identity is kept confidential"
                     )
    title          = models.CharField(max_length=255)
    description    = models.TextField(
                         help_text="Description of the violations observed on site"
                     )
    evidence_file  = models.FileField(
                         upload_to="reports/evidence/%Y/%m/",
                         blank=True,
                         help_text="Photo or video evidence uploaded by the reporter"
                     )
    status         = models.CharField(
                         max_length=20,
                         choices=ReportStatus.choices,
                         default=ReportStatus.PENDING
                     )
    admin_response = models.TextField(
                         blank=True,
                         help_text="Official admin response to the report"
                     )
    reviewed_by    = models.ForeignKey(
                         User,
                         on_delete=models.SET_NULL,
                         null=True, blank=True,
                         related_name="reports_reviewed",
                         limit_choices_to={"role": User.Role.ADMIN}
                     )
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        reporter = "Anonymous" if self.is_anonymous else getattr(self.reported_by, "username", "?")
        return f"Report by {reporter}  -  '{self.project.title}'"

    class Meta:
        verbose_name        = "Discrepancy Report"
        verbose_name_plural = "Discrepancy Reports"
        ordering            = ["-created_at"]
