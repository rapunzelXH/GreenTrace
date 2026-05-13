# greentrace/api/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from greentrace.models import (
    EcoMilestone, CarbonData, DiscrepancyReport,
    ExtensionRequest, AuditLog, CompanyProfile, Project,
)


# ── Helper ────────────────────────────────────────────────────────

def _log(user, action, model_name, object_id, details=None):
    AuditLog.objects.create(
        user=user, action=action, model_name=model_name,
        object_id=object_id, details=details or {},
    )


# ── UC-20: Eco-Score recalculation ───────────────────────────────

def _recalculate_eco_score(project):
    winning = project.winning_business
    if not winning:
        return
    milestones      = project.milestones.all()
    total_weight    = sum(m.weight for m in milestones) or 1
    approved_weight = sum(m.weight for m in milestones if m.status == "APPROVED")
    new_score       = round((approved_weight / total_weight) * 100, 2)
    CompanyProfile.objects.filter(pk=winning.pk).update(eco_score=new_score)
    _log(None, f"Eco-Score updated to {new_score} for {winning.company_name}",
         "CompanyProfile", winning.pk,
         {"project_id": project.pk, "new_score": new_score,
          "approved_weight": approved_weight, "total_weight": total_weight})


@receiver(post_save, sender=EcoMilestone)
def milestone_post_save(sender, instance, created, **kwargs):
    if instance.status in ("APPROVED", "REJECTED"):
        _recalculate_eco_score(instance.project)
    if not created:
        _log(instance.reviewed_by,
             f"Milestone '{instance.title}' status → {instance.status}",
             "EcoMilestone", instance.pk,
             {"project_id": instance.project.pk, "status": instance.status})


# ── UC-21: Carbon violation alert ────────────────────────────────

CO2_MONTHLY_LIMIT_KG = 5000.0


@receiver(pre_save, sender=CarbonData)
def carbon_data_pre_save(sender, instance, **kwargs):
    instance.calculate_co2()
    if instance.total_co2_kg and instance.total_co2_kg > CO2_MONTHLY_LIMIT_KG:
        instance.exceeds_limit = True


@receiver(post_save, sender=CarbonData)
def carbon_data_post_save(sender, instance, created, **kwargs):
    _log(instance.submitted_by,
         f"Carbon data: {instance.total_co2_kg:.1f} kg CO2 "
         f"{'⚠ EXCEEDS LIMIT' if instance.exceeds_limit else '✓ OK'}",
         "CarbonData", instance.pk,
         {"project_id": instance.project.pk,
          "period": f"{instance.period_month:02d}/{instance.period_year}",
          "total_co2_kg": instance.total_co2_kg,
          "exceeds_limit": instance.exceeds_limit})
    # Dispatch Celery email task if limit exceeded
    if instance.exceeds_limit:
        from greentrace.api.tasks import send_carbon_violation_alert
        send_carbon_violation_alert.delay(instance.pk)


# ── UC-16: Red flag on project ───────────────────────────────────

@receiver(post_save, sender=DiscrepancyReport)
def discrepancy_report_post_save(sender, instance, created, **kwargs):
    if created:
        Project.objects.filter(pk=instance.project.pk).update(has_red_flag=True)
        _log(instance.reported_by,
             f"Red Flag set on project '{instance.project.title}'",
             "DiscrepancyReport", instance.pk,
             {"project_id": instance.project.pk, "is_anonymous": instance.is_anonymous})
        # Dispatch Celery email task
        from greentrace.api.tasks import send_red_flag_alert
        send_red_flag_alert.delay(instance.pk)


# ── UC-14: Update milestone deadline after extension approved ─────

@receiver(post_save, sender=ExtensionRequest)
def extension_request_post_save(sender, instance, created, **kwargs):
    if not created and instance.status == "APPROVED":
        milestone    = instance.milestone
        old_deadline = milestone.deadline
        EcoMilestone.objects.filter(pk=milestone.pk).update(
            deadline=instance.proposed_deadline,
            status=EcoMilestone.MilestoneStatus.PENDING,
        )
        _log(instance.reviewed_by,
             f"Deadline extended for '{milestone.title}': "
             f"{old_deadline:%Y-%m-%d} → {instance.proposed_deadline:%Y-%m-%d}",
             "EcoMilestone", milestone.pk,
             {"old_deadline": str(old_deadline),
              "new_deadline": str(instance.proposed_deadline),
              "extension_req_id": instance.pk})
