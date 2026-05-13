# greentrace/api/serializers.py
#
# One serializer per model.
# Covers: UC-01 UC-03 UC-04 UC-05 UC-06 UC-08 UC-09 UC-10 UC-13 UC-16 UC-17

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

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


# ─────────────────────────────────────────────────────────────────
# AUTH SERIALIZERS  (UC-01, UC-02)
# ─────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """
    UC-01: User Registration.
    Validates email uniqueness, password strength and role selection.
    """
    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model  = User
        fields = ("id", "username", "email", "password", "password2", "role",
                  "first_name", "last_name")

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if data.get("role") not in ("BUSINESS", "JOURNALIST"):
            raise serializers.ValidationError(
                {"role": "Self-registration is only allowed for BUSINESS or JOURNALIST roles."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True          # set False if you want email-verify first
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Read-only user representation used in nested contexts."""
    class Meta:
        model  = User
        fields = ("id", "username", "email", "role", "first_name", "last_name",
                  "is_email_verified", "is_suspended", "date_joined")
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    """UC-03: Manage Profile — allows updating name and email."""
    class Meta:
        model  = User
        fields = ("first_name", "last_name", "email")


# ─────────────────────────────────────────────────────────────────
# COMPANY PROFILE  (UC-03)
# ─────────────────────────────────────────────────────────────────

class CompanyProfileSerializer(serializers.ModelSerializer):
    """
    UC-03: Register Company Profile.
    Business user creates / updates their company profile.
    eco_score is read-only — calculated automatically by the system.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model  = CompanyProfile
        fields = (
            "id", "user", "company_name", "registration_no", "address",
            "phone", "website", "iso_certificate", "qkb_document",
            "eco_score", "is_verified", "created_at",
        )
        read_only_fields = ("user", "eco_score", "is_verified", "created_at")

    def validate_registration_no(self, value):
        """NIPT must be unique — checked here for clear error messages."""
        qs = CompanyProfile.objects.filter(registration_no=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A company with this registration number already exists.")
        return value


class CompanyProfilePublicSerializer(serializers.ModelSerializer):
    """Public view — hides sensitive documents, shows eco_score only."""
    class Meta:
        model  = CompanyProfile
        fields = ("id", "company_name", "registration_no", "eco_score", "is_verified")


# ─────────────────────────────────────────────────────────────────
# PROJECT  (UC-04, UC-15)
# ─────────────────────────────────────────────────────────────────

class ProjectSerializer(serializers.ModelSerializer):
    """
    UC-04: Create New Tender (Admin).
    UC-15: Search Project Map (all users — read).
    """
    created_by       = UserSerializer(read_only=True)
    winning_business = CompanyProfilePublicSerializer(read_only=True)
    milestone_count  = serializers.SerializerMethodField()

    class Meta:
        model  = Project
        fields = (
            "id", "title", "description", "location",
            "latitude", "longitude", "status", "risk_level",
            "created_by", "winning_business",
            "submission_deadline", "start_date", "end_date", "budget",
            "has_red_flag", "milestone_count", "created_at", "updated_at",
        )
        read_only_fields = ("created_by", "winning_business", "has_red_flag",
                            "created_at", "updated_at")

    def get_milestone_count(self, obj):
        return obj.milestones.count()

    def validate_submission_deadline(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Submission deadline must be in the future.")
        return value


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views and map endpoints."""
    class Meta:
        model  = Project
        fields = ("id", "title", "location", "latitude", "longitude",
                  "status", "risk_level", "has_red_flag", "submission_deadline")


# ─────────────────────────────────────────────────────────────────
# ECO-MILESTONE  (UC-05)
# ─────────────────────────────────────────────────────────────────

class EcoMilestoneSerializer(serializers.ModelSerializer):
    """
    UC-05: Define Eco-Milestones.
    Admin defines milestones with deadlines, evidence types and weights.
    """
    reviewed_by = UserSerializer(read_only=True)
    is_overdue  = serializers.SerializerMethodField()

    class Meta:
        model  = EcoMilestone
        fields = (
            "id", "project", "title", "description", "evidence_type",
            "status", "deadline", "weight",
            "reviewed_by", "review_comment", "reviewed_at",
            "is_overdue", "created_at",
        )
        read_only_fields = ("reviewed_by", "reviewed_at", "created_at")

    def get_is_overdue(self, obj):
        return obj.is_overdue()

    def validate_weight(self, value):
        if not (1 <= value <= 100):
            raise serializers.ValidationError("Weight must be between 1 and 100.")
        return value


class MilestoneReviewSerializer(serializers.Serializer):
    """
    UC-11 / UC-12: Approve or Reject compliance proof.
    Used in a dedicated action endpoint — not a full model serializer.
    """
    action  = serializers.ChoiceField(choices=["approve", "reject"])
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data["action"] == "reject" and not data.get("comment"):
            raise serializers.ValidationError(
                {"comment": "A comment is required when rejecting proof."}
            )
        return data


# ─────────────────────────────────────────────────────────────────
# TENDER APPLICATION  (UC-06, UC-07)
# ─────────────────────────────────────────────────────────────────

class TenderApplicationSerializer(serializers.ModelSerializer):
    """
    UC-06: Apply for Green Tender (Business).
    UC-07: Review Business Bids (Admin — read + score).
    """
    business     = CompanyProfilePublicSerializer(read_only=True)
    evaluated_by = UserSerializer(read_only=True)

    class Meta:
        model  = TenderApplication
        fields = (
            "id", "project", "business",
            "status", "technical_proposal", "env_impact_statement",
            "financial_bid", "admin_score", "rejection_reason",
            "submitted_at", "evaluated_by", "created_at", "updated_at",
        )
        read_only_fields = (
            "business", "status", "admin_score", "rejection_reason",
            "submitted_at", "evaluated_by", "created_at", "updated_at",
        )

    def validate(self, data):
        from django.utils import timezone
        project = data.get("project") or (self.instance.project if self.instance else None)
        if project and project.submission_deadline < timezone.now():
            raise serializers.ValidationError(
                "The submission deadline for this tender has passed."
            )
        return data


class ApplicationEvaluateSerializer(serializers.Serializer):
    """
    UC-07: Admin scores and approves/rejects an application.
    Used in a dedicated action endpoint.
    """
    action           = serializers.ChoiceField(choices=["shortlist", "approve", "reject"])
    admin_score      = serializers.FloatField(min_value=0, max_value=100, required=False)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data["action"] == "reject" and not data.get("rejection_reason"):
            raise serializers.ValidationError(
                {"rejection_reason": "A rejection reason is required."}
            )
        return data


# ─────────────────────────────────────────────────────────────────
# COMPLIANCE EVIDENCE  (UC-08, UC-09)
# ─────────────────────────────────────────────────────────────────

class ComplianceEvidenceSerializer(serializers.ModelSerializer):
    """
    UC-08: Upload Photo Evidence (geotagged).
    UC-09: Upload Legal Documents.
    GPS metadata (gps_latitude, gps_longitude, captured_at) is extracted
    automatically in the view using Pillow/Exifread — not set by client.
    """
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model  = ComplianceEvidence
        fields = (
            "id", "milestone", "uploaded_by", "category", "file", "description",
            "gps_latitude", "gps_longitude", "captured_at", "gps_validated",
            "validity_date", "document_type", "uploaded_at",
        )
        read_only_fields = (
            "uploaded_by", "gps_latitude", "gps_longitude",
            "captured_at", "gps_validated", "uploaded_at",
        )

    def validate_file(self, value):
        allowed_photo = ("image/jpeg", "image/png", "image/webp")
        allowed_doc   = ("application/pdf",)
        content_type  = getattr(value, "content_type", "")
        category      = self.initial_data.get("category", "")

        if category == "PHOTO" and content_type not in allowed_photo:
            raise serializers.ValidationError("Photo evidence must be JPG, PNG or WEBP.")
        if category == "DOCUMENT" and content_type not in allowed_doc:
            raise serializers.ValidationError("Legal document must be a PDF file.")
        return value


# ─────────────────────────────────────────────────────────────────
# CARBON DATA  (UC-10)
# ─────────────────────────────────────────────────────────────────

class CarbonDataSerializer(serializers.ModelSerializer):
    """
    UC-10: Input Carbon Data.
    total_co2_kg is calculated automatically — not editable by user.
    """
    submitted_by = UserSerializer(read_only=True)

    class Meta:
        model  = CarbonData
        fields = (
            "id", "project", "submitted_by", "period_month", "period_year",
            "fuel_liters", "electricity_kwh",
            "total_co2_kg", "exceeds_limit", "created_at",
        )
        read_only_fields = ("submitted_by", "total_co2_kg", "exceeds_limit", "created_at")

    def validate(self, data):
        if data.get("fuel_liters", 0) < 0:
            raise serializers.ValidationError({"fuel_liters": "Cannot be negative."})
        if data.get("electricity_kwh", 0) < 0:
            raise serializers.ValidationError({"electricity_kwh": "Cannot be negative."})
        return data


# ─────────────────────────────────────────────────────────────────
# DISCREPANCY REPORT  (UC-16)
# ─────────────────────────────────────────────────────────────────

class DiscrepancyReportSerializer(serializers.ModelSerializer):
    """
    UC-16: Report Discrepancy (Whistleblowing).
    If is_anonymous=True, reported_by is hidden from public responses.
    """
    reported_by = serializers.SerializerMethodField()
    reviewed_by = UserSerializer(read_only=True)

    class Meta:
        model  = DiscrepancyReport
        fields = (
            "id", "project", "reported_by", "is_anonymous",
            "title", "description", "evidence_file",
            "status", "admin_response", "reviewed_by",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "reported_by", "status", "admin_response",
            "reviewed_by", "created_at", "updated_at",
        )

    def get_reported_by(self, obj):
        """Hide reporter identity if anonymous — UC-16 confidentiality."""
        if obj.is_anonymous:
            return "Anonymous"
        if obj.reported_by:
            return obj.reported_by.username
        return None


class ReportRespondSerializer(serializers.Serializer):
    """Admin responds to a discrepancy report."""
    status         = serializers.ChoiceField(
                         choices=["UNDER_REVIEW", "RESOLVED", "DISMISSED"])
    admin_response = serializers.CharField()


# ─────────────────────────────────────────────────────────────────
# PROJECT FOLLOW  (UC-17)
# ─────────────────────────────────────────────────────────────────

class ProjectFollowSerializer(serializers.ModelSerializer):
    """UC-17: Follow Project Updates."""
    user    = UserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), source="project", write_only=True
    )

    class Meta:
        model  = ProjectFollow
        fields = ("id", "user", "project", "project_id", "frequency", "followed_at")
        read_only_fields = ("user", "followed_at")

    def validate(self, data):
        user    = self.context["request"].user
        project = data["project"]
        if ProjectFollow.objects.filter(user=user, project=project).exists():
            raise serializers.ValidationError("You are already following this project.")
        return data


# ─────────────────────────────────────────────────────────────────
# EXTENSION REQUEST  (UC-13, UC-14)
# ─────────────────────────────────────────────────────────────────

class ExtensionRequestSerializer(serializers.ModelSerializer):
    """
    UC-13: Request Deadline Extension (Business).
    UC-14: Approve / Reject Extension (Admin).
    """
    requested_by = UserSerializer(read_only=True)
    reviewed_by  = UserSerializer(read_only=True)

    class Meta:
        model  = ExtensionRequest
        fields = (
            "id", "milestone", "requested_by",
            "proposed_deadline", "justification", "justification_doc",
            "status", "admin_comment", "reviewed_by",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "requested_by", "status", "admin_comment",
            "reviewed_by", "created_at", "updated_at",
        )

    def validate(self, data):
        from django.utils import timezone
        milestone = data.get("milestone") or (self.instance.milestone if self.instance else None)

        # UC-13: cannot request if already overdue
        if milestone and milestone.deadline < timezone.now():
            raise serializers.ValidationError(
                "Cannot request an extension after the milestone deadline has passed."
            )
        # only one extension per milestone
        if milestone and ExtensionRequest.objects.filter(
            milestone=milestone
        ).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError(
                "An extension request already exists for this milestone."
            )
        return data


class ExtensionReviewSerializer(serializers.Serializer):
    """Admin approves or rejects the extension request."""
    action        = serializers.ChoiceField(choices=["approve", "reject"])
    admin_comment = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data["action"] == "reject" and not data.get("admin_comment"):
            raise serializers.ValidationError(
                {"admin_comment": "A comment is required when rejecting an extension."}
            )
        return data


# ─────────────────────────────────────────────────────────────────
# AUDIT LOG  (FR_10, FR_38) — read only
# ─────────────────────────────────────────────────────────────────

class AuditLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model  = AuditLog
        fields = ("id", "user", "action", "model_name", "object_id",
                  "details", "ip_address", "timestamp")
        read_only_fields = fields


# ─────────────────────────────────────────────────────────────────
# ECO-SCORE COMPARISON  (UC-18)
# ─────────────────────────────────────────────────────────────────

class EcoScoreCompareSerializer(serializers.Serializer):
    """
    UC-18: Compare Eco-Scores.
    Input: list of company IDs to compare.
    """
    company_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        max_length=5,
        help_text="List of CompanyProfile IDs to compare (2–5)."
    )
