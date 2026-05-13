# greentrace/api/tasks.py
#
# Celery background tasks — Phase 2
#
# UC-21: Check overdue milestones every 24h
# UC-17: Send weekly notification digest
# UC-16: Red Flag email alert to admin
#
# Run worker:  celery -A config worker -l info
# Run beat:    celery -A config beat   -l info

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta


# ─────────────────────────────────────────────────────────────────
# UC-21: CHECK OVERDUE MILESTONES  (runs every 24h via Celery Beat)
# ─────────────────────────────────────────────────────────────────

@shared_task(name="greentrace.check_overdue_milestones")
def check_overdue_milestones():
    """
    UC-21: System monitors the database for expired deadlines every 24h.
    Marks PENDING milestones as OVERDUE and logs them to AuditLog.
    Sends email alert to the assigned Admin and the Business.
    """
    from greentrace.models import EcoMilestone, AuditLog

    now      = timezone.now()
    overdue  = EcoMilestone.objects.filter(
        status   = EcoMilestone.MilestoneStatus.PENDING,
        deadline__lt = now,
    ).select_related("project", "project__winning_business",
                     "project__winning_business__user",
                     "project__created_by")

    count = 0
    for milestone in overdue:
        # Mark as OVERDUE
        EcoMilestone.objects.filter(pk=milestone.pk).update(
            status=EcoMilestone.MilestoneStatus.OVERDUE
        )

        # AuditLog entry
        AuditLog.objects.create(
            user       = None,
            action     = f"Milestone '{milestone.title}' automatically marked OVERDUE",
            model_name = "EcoMilestone",
            object_id  = milestone.pk,
            details    = {
                "project_id"  : milestone.project.pk,
                "deadline"    : str(milestone.deadline),
                "days_overdue": (now - milestone.deadline).days,
            },
        )

        # Email alert to admin (UC-21)
        admin_email = getattr(milestone.project.created_by, "email", None)
        if admin_email:
            _send_overdue_alert_admin(milestone, admin_email)

        # Email alert to business contractor
        business = milestone.project.winning_business
        if business and business.user.email:
            _send_overdue_alert_business(milestone, business.user.email)

        count += 1

    return f"Marked {count} milestones as OVERDUE"


def _send_overdue_alert_admin(milestone, admin_email):
    """Send overdue milestone notification to Admin."""
    try:
        send_mail(
            subject = f"[GreenTrace] ⚠ Overdue Milestone: {milestone.title}",
            message = (
                f"The following milestone has passed its deadline without submission:\n\n"
                f"Project   : {milestone.project.title}\n"
                f"Milestone : {milestone.title}\n"
                f"Deadline  : {milestone.deadline:%Y-%m-%d %H:%M}\n\n"
                f"Please review the project and take appropriate action.\n"
            ),
            from_email    = settings.DEFAULT_FROM_EMAIL,
            recipient_list= [admin_email],
            fail_silently = True,
        )
    except Exception:
        pass


def _send_overdue_alert_business(milestone, business_email):
    """Send overdue milestone notification to Business contractor."""
    try:
        send_mail(
            subject = f"[GreenTrace] Action Required: Milestone '{milestone.title}' is Overdue",
            message = (
                f"Your milestone has passed its deadline:\n\n"
                f"Project   : {milestone.project.title}\n"
                f"Milestone : {milestone.title}\n"
                f"Deadline  : {milestone.deadline:%Y-%m-%d %H:%M}\n\n"
                f"Please upload your evidence immediately or request a deadline extension.\n"
            ),
            from_email    = settings.DEFAULT_FROM_EMAIL,
            recipient_list= [business_email],
            fail_silently = True,
        )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────
# UC-17: WEEKLY NOTIFICATION DIGEST  (runs every Monday 08:00)
# ─────────────────────────────────────────────────────────────────

@shared_task(name="greentrace.send_weekly_digest")
def send_weekly_digest():
    """
    UC-17: Sends a weekly summary email to users who follow projects
    with frequency=WEEKLY.
    Includes: new milestones, status changes, red flags this week.
    """
    from greentrace.models import ProjectFollow, EcoMilestone, Project

    one_week_ago = timezone.now() - timedelta(days=7)

    follows = ProjectFollow.objects.filter(
        frequency="WEEKLY"
    ).select_related("user", "project")

    sent = 0
    for follow in follows:
        user    = follow.user
        project = follow.project

        # Collect updates for this project in the last week
        new_milestones = EcoMilestone.objects.filter(
            project    = project,
            created_at__gte = one_week_ago,
        ).count()

        status_changes = EcoMilestone.objects.filter(
            project      = project,
            reviewed_at__gte = one_week_ago,
        ).count()

        if new_milestones == 0 and status_changes == 0:
            continue  # no updates to report

        try:
            send_mail(
                subject = f"[GreenTrace] Weekly Update: {project.title}",
                message = (
                    f"Weekly summary for project: {project.title}\n\n"
                    f"New milestones this week   : {new_milestones}\n"
                    f"Milestone status changes   : {status_changes}\n"
                    f"Current project status     : {project.get_status_display()}\n"
                    f"Risk level                 : {project.get_risk_level_display()}\n"
                    f"Red Flag                   : {'YES ⚠' if project.has_red_flag else 'No'}\n\n"
                    f"View project: http://localhost:3000/projects/{project.pk}\n"
                ),
                from_email    = settings.DEFAULT_FROM_EMAIL,
                recipient_list= [user.email],
                fail_silently = True,
            )
            sent += 1
        except Exception:
            pass

    return f"Sent {sent} weekly digest emails"


# ─────────────────────────────────────────────────────────────────
# UC-21: CARBON VIOLATION EMAIL ALERT  (triggered from signal)
# ─────────────────────────────────────────────────────────────────

@shared_task(name="greentrace.send_carbon_violation_alert")
def send_carbon_violation_alert(carbon_data_id):
    """
    UC-21: Sends email when carbon data exceeds monthly limit.
    Called from signals.py post_save of CarbonData.
    """
    from greentrace.models import CarbonData

    try:
        record  = CarbonData.objects.select_related(
            "project", "project__created_by", "submitted_by"
        ).get(pk=carbon_data_id)
    except CarbonData.DoesNotExist:
        return

    admin_email    = record.project.created_by.email
    business_email = record.submitted_by.email

    message = (
        f"Carbon footprint limit exceeded!\n\n"
        f"Project  : {record.project.title}\n"
        f"Period   : {record.period_month:02d}/{record.period_year}\n"
        f"CO2 Total: {record.total_co2_kg:.1f} kg\n"
        f"Limit    : 5000.0 kg\n\n"
        f"Submitted by: {record.submitted_by.username}\n"
    )

    for email in [admin_email, business_email]:
        if email:
            try:
                send_mail(
                    subject       = f"[GreenTrace] ⚠ Carbon Limit Exceeded — {record.project.title}",
                    message       = message,
                    from_email    = settings.DEFAULT_FROM_EMAIL,
                    recipient_list= [email],
                    fail_silently = True,
                )
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────
# UC-16: RED FLAG EMAIL TO ADMIN  (triggered from signal)
# ─────────────────────────────────────────────────────────────────

@shared_task(name="greentrace.send_red_flag_alert")
def send_red_flag_alert(report_id):
    """
    UC-16: Notifies Admin when a new discrepancy report is submitted.
    Called from signals.py post_save of DiscrepancyReport.
    """
    from greentrace.models import DiscrepancyReport

    try:
        report = DiscrepancyReport.objects.select_related(
            "project", "project__created_by"
        ).get(pk=report_id)
    except DiscrepancyReport.DoesNotExist:
        return

    admin_email = report.project.created_by.email
    if not admin_email:
        return

    reporter = "Anonymous" if report.is_anonymous else getattr(
        report.reported_by, "username", "Unknown"
    )

    try:
        send_mail(
            subject = f"[GreenTrace] 🚩 Red Flag Report: {report.project.title}",
            message = (
                f"A new discrepancy report has been submitted:\n\n"
                f"Project   : {report.project.title}\n"
                f"Title     : {report.title}\n"
                f"Reporter  : {reporter}\n"
                f"Submitted : {report.created_at:%Y-%m-%d %H:%M}\n\n"
                f"Description:\n{report.description}\n\n"
                f"Please review at: http://localhost:3000/admin/reports/{report.pk}\n"
            ),
            from_email    = settings.DEFAULT_FROM_EMAIL,
            recipient_list= [admin_email],
            fail_silently = True,
        )
    except Exception:
        pass
