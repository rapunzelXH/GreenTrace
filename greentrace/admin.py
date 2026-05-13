# greentrace/admin.py
# Registers all models in the Django admin panel.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from greentrace.models import (
    User,
    CompanyProfile,
    Project,
    EcoMilestone,
    TenderApplication,
    ComplianceEvidence,
    CarbonData,
    DiscrepancyReport,
    ProjectFollow,
    AuditLog,
    ExtensionRequest,
)


# ── User ─────────────────────────────────────────────────────────
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ("username", "email", "role", "is_email_verified", "is_suspended", "date_joined")
    list_filter   = ("role", "is_email_verified", "is_suspended", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering      = ("-date_joined",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("GreenTrace", {
            "fields": ("role", "is_email_verified", "is_suspended", "failed_login_count")
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("GreenTrace", {
            "fields": ("role",)
        }),
    )


# ── Company Profile ───────────────────────────────────────────────
@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display    = ("company_name", "registration_no", "eco_score", "is_verified", "created_at")
    list_filter     = ("is_verified",)
    search_fields   = ("company_name", "registration_no", "user__email")
    readonly_fields = ("eco_score", "created_at")


# ── Project ───────────────────────────────────────────────────────
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display    = ("title", "status", "risk_level", "location", "submission_deadline", "has_red_flag", "created_at")
    list_filter     = ("status", "risk_level", "has_red_flag")
    search_fields   = ("title", "location", "description")
    date_hierarchy  = "created_at"
    readonly_fields = ("created_at", "updated_at")


# ── Eco-Milestone ─────────────────────────────────────────────────
@admin.register(EcoMilestone)
class EcoMilestoneAdmin(admin.ModelAdmin):
    list_display    = ("title", "project", "status", "evidence_type", "deadline", "weight")
    list_filter     = ("status", "evidence_type")
    search_fields   = ("title", "project__title")
    readonly_fields = ("created_at",)


# ── Tender Application ────────────────────────────────────────────
@admin.register(TenderApplication)
class TenderApplicationAdmin(admin.ModelAdmin):
    list_display    = ("business", "project", "status", "financial_bid", "admin_score", "submitted_at")
    list_filter     = ("status",)
    search_fields   = ("business__company_name", "project__title")
    readonly_fields = ("created_at", "updated_at")


# ── Compliance Evidence ───────────────────────────────────────────
@admin.register(ComplianceEvidence)
class ComplianceEvidenceAdmin(admin.ModelAdmin):
    list_display    = ("milestone", "uploaded_by", "category", "gps_validated", "uploaded_at")
    list_filter     = ("category", "gps_validated")
    search_fields   = ("milestone__title", "uploaded_by__username")
    readonly_fields = ("uploaded_at", "gps_latitude", "gps_longitude", "captured_at")


# ── Carbon Data ───────────────────────────────────────────────────
@admin.register(CarbonData)
class CarbonDataAdmin(admin.ModelAdmin):
    list_display    = ("project", "period_month", "period_year", "fuel_liters", "electricity_kwh", "total_co2_kg", "exceeds_limit")
    list_filter     = ("exceeds_limit", "period_year")
    search_fields   = ("project__title",)
    readonly_fields = ("total_co2_kg", "created_at")


# ── Discrepancy Report ────────────────────────────────────────────
@admin.register(DiscrepancyReport)
class DiscrepancyReportAdmin(admin.ModelAdmin):
    list_display    = ("title", "project", "is_anonymous", "status", "created_at")
    list_filter     = ("status", "is_anonymous")
    search_fields   = ("title", "description", "project__title")
    readonly_fields = ("created_at", "updated_at")


# ── Project Follow ────────────────────────────────────────────────
@admin.register(ProjectFollow)
class ProjectFollowAdmin(admin.ModelAdmin):
    list_display    = ("user", "project", "frequency", "followed_at")
    list_filter     = ("frequency",)
    search_fields   = ("user__username", "project__title")
    readonly_fields = ("followed_at",)


# ── Audit Log — read only, never created/modified manually ────────
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display    = ("timestamp", "user", "action", "model_name", "object_id", "ip_address")
    list_filter     = ("model_name",)
    search_fields   = ("user__username", "action", "model_name")
    date_hierarchy  = "timestamp"
    readonly_fields = ("timestamp", "user", "action", "model_name", "object_id", "details", "ip_address")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ── Extension Request ─────────────────────────────────────────────
@admin.register(ExtensionRequest)
class ExtensionRequestAdmin(admin.ModelAdmin):
    list_display    = ("milestone", "requested_by", "proposed_deadline", "status", "created_at")
    list_filter     = ("status",)
    search_fields   = ("milestone__title", "requested_by__username")
    readonly_fields = ("created_at", "updated_at")
