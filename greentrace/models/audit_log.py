# greentrace/models/audit_log.py
# FR_10: Log all user activities
# FR_38: Digital Audit Trail for every project

from django.db import models

from .user import User


class AuditLog(models.Model):
    """
    Immutable digital trail for every action in the system.

    Recorded automatically by signals or middleware,
    not directly by the user.

    Fields:
      model_name  - name of the Django class (e.g. "Project", "EcoMilestone")
      object_id   - PK of the changed object
      details     - JSON with old/new values
      ip_address  - client IP at the time of the action
    """

    user       = models.ForeignKey(
                     User,
                     on_delete=models.SET_NULL,
                     null=True, blank=True,
                     related_name="audit_logs",
                     help_text="NULL if the action is system-generated (automatic)"
                 )
    action     = models.CharField(
                     max_length=255,
                     help_text="Short description of the action (e.g. 'Milestone APPROVED')"
                 )
    model_name = models.CharField(
                     max_length=100,
                     help_text="Affected Django class (e.g. 'EcoMilestone')"
                 )
    object_id  = models.PositiveIntegerField(
                     null=True, blank=True,
                     help_text="Primary key of the changed object"
                 )
    details    = models.JSONField(
                     default=dict, blank=True,
                     help_text="Additional details such as before/after values"
                 )
    ip_address = models.GenericIPAddressField(
                     null=True, blank=True,
                     help_text="HTTP client IP at the time of the action"
                 )
    timestamp  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        actor = self.user.username if self.user else "System"
        return f"[{self.timestamp:%Y-%m-%d %H:%M}]  {actor}:  {self.action}"

    class Meta:
        verbose_name        = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering            = ["-timestamp"]
