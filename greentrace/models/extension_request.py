# greentrace/models/extension_request.py
# UC-13: Request Deadline Extension (by business)
# UC-14: Approve / Reject Postpone Request (by admin)
# FR_26: Businesses request deadline extensions with justification
# FR_34: Admin approves or rejects the request

from django.db import models

from .user import User
from .eco_milestone import EcoMilestone


class ExtensionRequest(models.Model):
    """
    Deadline extension request for a specific milestone.

    Policy rules (NFR):
      - Only one request allowed per milestone
        (unless SuperAdmin authorises more).
      - Request can only be made BEFORE the current deadline expires.

    Flow:
        PENDING  ->  APPROVED  (milestone deadline updated automatically)
                 ->  REJECTED  (original deadline remains)
    """

    class ExtStatus(models.TextChoices):
        PENDING  = "PENDING",  "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    milestone         = models.ForeignKey(
                            EcoMilestone,
                            on_delete=models.CASCADE,
                            related_name="extension_requests"
                        )
    requested_by      = models.ForeignKey(
                            User,
                            on_delete=models.PROTECT,
                            related_name="extension_requests"
                        )
    proposed_deadline = models.DateTimeField(
                            help_text="New proposed deadline submitted by the business"
                        )
    justification     = models.TextField(
                            help_text="Business justification for the extension request"
                        )
    justification_doc = models.FileField(
                            upload_to="extensions/docs/",
                            blank=True,
                            help_text="Supporting document (e.g. weather report, invoice)"
                        )
    status            = models.CharField(
                            max_length=10,
                            choices=ExtStatus.choices,
                            default=ExtStatus.PENDING
                        )
    admin_comment     = models.TextField(
                            blank=True,
                            help_text="Admin comment during approval or rejection"
                        )
    reviewed_by       = models.ForeignKey(
                            User,
                            on_delete=models.SET_NULL,
                            null=True, blank=True,
                            related_name="extensions_reviewed",
                            limit_choices_to={"role": User.Role.ADMIN}
                        )
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Extension Request:  {self.milestone.title}"
            f"  [{self.get_status_display()}]"
        )

    class Meta:
        verbose_name        = "Extension Request"
        verbose_name_plural = "Extension Requests"
