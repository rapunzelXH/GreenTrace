# greentrace/models/project_follow.py
# UC-17: Follow Project Updates
# FR_16: Subscription feature - user receives automated notifications

from django.db import models

from .user import User
from .project import Project


class ProjectFollow(models.Model):
    """
    A user's subscription to notifications for a specific project.

    Notification frequency:
      REALTIME - immediate notifications on any change
      WEEKLY   - weekly digest summary

    The (user, project) pair is unique - a user
    can follow a project only once.
    """

    class Frequency(models.TextChoices):
        REALTIME = "REALTIME", "Real-time"
        WEEKLY   = "WEEKLY",   "Weekly"

    user        = models.ForeignKey(
                      User,
                      on_delete=models.CASCADE,
                      related_name="followed_projects"
                  )
    project     = models.ForeignKey(
                      Project,
                      on_delete=models.CASCADE,
                      related_name="followers"
                  )
    frequency   = models.CharField(
                      max_length=10,
                      choices=Frequency.choices,
                      default=Frequency.REALTIME
                  )
    followed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}  follows  '{self.project.title}'  ({self.get_frequency_display()})"

    class Meta:
        verbose_name        = "Project Follow"
        verbose_name_plural = "Project Follows"
        unique_together     = ("user", "project")
