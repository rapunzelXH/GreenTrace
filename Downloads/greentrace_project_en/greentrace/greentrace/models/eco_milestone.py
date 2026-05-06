# greentrace/models/eco_milestone.py
# FR_31: Admin defines eco-milestones with deadlines and evidence types
# FR_28: Monitor Milestones | UC-11/12: Approve / Reject proof

from django.db import models
from django.utils import timezone

from .user import User
from .project import Project


class EcoMilestone(models.Model):
    """
    Environmental milestone linked to a specific project.

    Each project has one or more milestones.
    The weight of each milestone directly affects
    the business Eco-Score calculation (FR_41).

    Possible statuses:
        PENDING  ->  SUBMITTED  ->  APPROVED
                               ->  REJECTED  ->  ACTION_REQUIRED
        PENDING  ->  OVERDUE        (set automatically by the system)
        PENDING  ->  EXTENSION_PENDING  (after UC-13)
    """

    class EvidenceType(models.TextChoices):
        PHOTO    = "PHOTO",    "Geotagged Photo"
        DOCUMENT = "DOCUMENT", "Legal Document (PDF)"
        BOTH     = "BOTH",     "Photo and Document"
        REPORT   = "REPORT",   "Technical Report"

    class MilestoneStatus(models.TextChoices):
        PENDING           = "PENDING",           "Pending"
        SUBMITTED         = "SUBMITTED",         "Submitted (Under Review)"
        APPROVED          = "APPROVED",          "Approved"
        REJECTED          = "REJECTED",          "Rejected"
        OVERDUE           = "OVERDUE",           "Overdue"
        ACTION_REQUIRED   = "ACTION_REQUIRED",   "Action Required"
        EXTENSION_PENDING = "EXTENSION_PENDING", "Extension Request Pending"

    project        = models.ForeignKey(
                         Project,
                         on_delete=models.CASCADE,
                         related_name="milestones"
                     )
    title          = models.CharField(max_length=255)
    description    = models.TextField()
    evidence_type  = models.CharField(
                         max_length=20,
                         choices=EvidenceType.choices,
                         help_text="Type of evidence required from the business"
                     )
    status         = models.CharField(
                         max_length=25,
                         choices=MilestoneStatus.choices,
                         default=MilestoneStatus.PENDING
                     )
    deadline       = models.DateTimeField(help_text="Deadline for submitting evidence")
    weight         = models.PositiveSmallIntegerField(
                         default=10,
                         help_text="Weight for Eco-Score calculation — all weights should sum to 100"
                     )
    reviewed_by    = models.ForeignKey(
                         User,
                         on_delete=models.SET_NULL,
                         null=True, blank=True,
                         related_name="milestones_reviewed",
                         limit_choices_to={"role": User.Role.ADMIN}
                     )
    review_comment = models.TextField(
                         blank=True,
                         help_text="Admin comment during approval / rejection"
                     )
    reviewed_at    = models.DateTimeField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def is_overdue(self) -> bool:
        """Returns True if milestone is still PENDING and the deadline has passed."""
        return (
            self.status == self.MilestoneStatus.PENDING
            and timezone.now() > self.deadline
        )

    def __str__(self):
        return f"{self.project.title}  —  {self.title}  [{self.get_status_display()}]"

    class Meta:
        verbose_name        = "Eco-Milestone"
        verbose_name_plural = "Eco-Milestones"
        ordering            = ["deadline"]
