# greentrace/api/views.py
#
# ViewSets for all models — Phase 1 complete.
# Covers all 21 Use Cases from the GreenTrace specification.

from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from greentrace.models import (
    CompanyProfile, Project, EcoMilestone,
    TenderApplication, ComplianceEvidence, CarbonData,
    DiscrepancyReport, ProjectFollow, AuditLog, ExtensionRequest,
)
from .serializers import (
    RegisterSerializer, UserSerializer, UserUpdateSerializer,
    CompanyProfileSerializer, CompanyProfilePublicSerializer,
    ProjectSerializer, ProjectListSerializer,
    EcoMilestoneSerializer, MilestoneReviewSerializer,
    TenderApplicationSerializer, ApplicationEvaluateSerializer,
    ComplianceEvidenceSerializer,
    CarbonDataSerializer,
    DiscrepancyReportSerializer, ReportRespondSerializer,
    ProjectFollowSerializer,
    ExtensionRequestSerializer, ExtensionReviewSerializer,
    AuditLogSerializer, EcoScoreCompareSerializer,
)
from .permissions import IsAdmin, IsBusiness

User = get_user_model()


# ─────────────────────────────────────────────────────────────────
# HELPER: extract GPS from image EXIF  (UC-08, FR_43)
# ─────────────────────────────────────────────────────────────────

def _extract_gps(file_obj):
    """
    Extracts GPS latitude, longitude and capture timestamp
    from image EXIF data using Pillow.
    Returns (lat, lon, datetime) or (None, None, None).
    """
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS
        import datetime

        img  = Image.open(file_obj)
        exif = img._getexif()
        if not exif:
            return None, None, None

        gps_info    = {}
        captured_at = None

        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_tag_id, gps_value in value.items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag] = gps_value
            if tag == "DateTimeOriginal":
                try:
                    captured_at = datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    captured_at = timezone.make_aware(captured_at)
                except Exception:
                    pass

        def _to_decimal(dms, ref):
            d, m, s = dms
            decimal = float(d) + float(m) / 60 + float(s) / 3600
            if ref in ("S", "W"):
                decimal = -decimal
            return round(decimal, 6)

        lat = lon = None
        if "GPSLatitude" in gps_info and "GPSLatitudeRef" in gps_info:
            lat = _to_decimal(gps_info["GPSLatitude"], gps_info["GPSLatitudeRef"])
        if "GPSLongitude" in gps_info and "GPSLongitudeRef" in gps_info:
            lon = _to_decimal(gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"])

        return lat, lon, captured_at

    except Exception:
        return None, None, None


def _validate_gps_against_project(lat, lon, project, tolerance_km=1.0):
    """
    Returns True if the photo GPS coordinates are within
    tolerance_km of the project site coordinates.
    """
    if lat is None or lon is None:
        return False
    if project.latitude is None or project.longitude is None:
        return False
    try:
        import math
        R    = 6371
        dlat = math.radians(float(project.latitude)  - lat)
        dlon = math.radians(float(project.longitude) - lon)
        a    = (math.sin(dlat / 2) ** 2
                + math.cos(math.radians(lat))
                * math.cos(math.radians(float(project.latitude)))
                * math.sin(dlon / 2) ** 2)
        return R * 2 * math.asin(math.sqrt(a)) <= tolerance_km
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────
# UC-01: USER REGISTRATION
# ─────────────────────────────────────────────────────────────────

class RegisterViewSet(viewsets.GenericViewSet):
    """POST /api/auth/register/"""
    serializer_class   = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "Account created. Please verify your email.", "id": user.pk},
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────────────────────────
# UC-03: USER PROFILE  (view + update own profile)
# ─────────────────────────────────────────────────────────────────

class UserProfileViewSet(viewsets.GenericViewSet):
    """
    GET /api/auth/me/  — view own profile
    PUT /api/auth/me/  — update name/email
    No pk needed — always operates on request.user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = UserSerializer   # default; overridden per action

    def list(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)

    def update(self, request, *args, **kwargs):
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ─────────────────────────────────────────────────────────────────
# UC-03: COMPANY PROFILE
# ─────────────────────────────────────────────────────────────────

class CompanyProfileViewSet(viewsets.ModelViewSet):
    """
    GET    /api/companies/          — public list
    GET    /api/companies/{id}/     — public detail
    POST   /api/companies/          — Business creates profile (UC-03)
    PUT    /api/companies/{id}/     — Business updates profile
    POST   /api/companies/compare/  — UC-18 compare eco-scores
    """
    queryset       = CompanyProfile.objects.select_related("user").all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.request.user.is_authenticated and self.request.user.role == "BUSINESS":
            return CompanyProfileSerializer
        return CompanyProfilePublicSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsBusiness()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def compare(self, request):
        """UC-18: Compare Eco-Scores side by side."""
        ser = EcoScoreCompareSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        companies = CompanyProfile.objects.filter(
            pk__in=ser.validated_data["company_ids"]
        ).values("id", "company_name", "eco_score", "is_verified")
        return Response(list(companies))


# ─────────────────────────────────────────────────────────────────
# UC-04, UC-15, UC-24: PROJECT
# ─────────────────────────────────────────────────────────────────

class ProjectViewSet(viewsets.ModelViewSet):
    """
    UC-04: Admin creates tender.
    UC-15: Map / list view for journalists.
    UC-24: Admin manages (edit/delete) projects.
    """
    queryset        = Project.objects.select_related("created_by", "winning_business").all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields   = ["title", "location", "description"]
    ordering_fields = ["created_at", "submission_deadline", "risk_level"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        return ProjectSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        status_p   = self.request.query_params.get("status")
        risk_p     = self.request.query_params.get("risk_level")
        location_p = self.request.query_params.get("location")
        if status_p:
            qs = qs.filter(status=status_p)
        if risk_p:
            qs = qs.filter(risk_level=risk_p)
        if location_p:
            qs = qs.filter(location__icontains=location_p)
        return qs

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def map(self, request):
        """UC-15: GeoJSON endpoint for the interactive map."""
        projects = Project.objects.filter(
            status__in=["OPEN", "REVIEW", "EXECUTION", "COMPLETED"]
        ).exclude(latitude=None).values(
            "id", "title", "latitude", "longitude",
            "status", "risk_level", "has_red_flag",
        )
        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type"       : "Point",
                    "coordinates": [float(p["longitude"]), float(p["latitude"])],
                },
                "properties": {
                    "id"        : p["id"],
                    "title"     : p["title"],
                    "status"    : p["status"],
                    "risk_level": p["risk_level"],
                    "red_flag"  : p["has_red_flag"],
                },
            }
            for p in projects
        ]
        return Response({"type": "FeatureCollection", "features": features})

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def milestones(self, request, pk=None):
        """List milestones for a specific project."""
        project    = self.get_object()
        milestones = project.milestones.all()
        return Response(EcoMilestoneSerializer(milestones, many=True).data)


# ─────────────────────────────────────────────────────────────────
# UC-05, UC-11, UC-12: ECO-MILESTONE
# ─────────────────────────────────────────────────────────────────

class EcoMilestoneViewSet(viewsets.ModelViewSet):
    """
    UC-05:  Admin defines milestones.
    UC-11:  Admin approves compliance proof.
    UC-12:  Admin rejects compliance proof.
    """
    queryset           = EcoMilestone.objects.select_related("project", "reviewed_by").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return EcoMilestoneSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "review"):
            return [IsAdmin()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        """
        UC-11 / UC-12: Approve or reject evidence.
        Signal recalculates Eco-Score automatically after save.
        """
        # manual permission check — @action inherits class-level [IsAuthenticated]
        if request.user.role != "ADMIN":
            return Response(
                {"detail": "Only admins can review milestones."},
                status=status.HTTP_403_FORBIDDEN,
            )

        milestone  = self.get_object()
        serializer = MilestoneReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        act     = serializer.validated_data["action"]
        comment = serializer.validated_data.get("comment", "")

        milestone.status         = (EcoMilestone.MilestoneStatus.APPROVED
                                    if act == "approve"
                                    else EcoMilestone.MilestoneStatus.REJECTED)
        milestone.reviewed_by    = request.user
        milestone.review_comment = comment
        milestone.reviewed_at    = timezone.now()
        milestone.save()  # triggers signal -> Eco-Score recalculation

        return Response(EcoMilestoneSerializer(milestone).data)


# ─────────────────────────────────────────────────────────────────
# UC-06, UC-07: TENDER APPLICATION
# ─────────────────────────────────────────────────────────────────

class TenderApplicationViewSet(viewsets.ModelViewSet):
    """
    UC-06: Business submits application.
    UC-07: Admin evaluates bids.
    """
    queryset       = TenderApplication.objects.select_related(
                         "project", "business", "evaluated_by"
                     ).all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        return TenderApplicationSerializer

    def get_permissions(self):
        if self.action == "evaluate":
            return [IsAdmin()]
        if self.action in ("create", "submit"):
            return [IsBusiness()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs   = super().get_queryset()
        user = self.request.user
        if user.role == "BUSINESS":
            try:
                return qs.filter(business=user.company_profile)
            except CompanyProfile.DoesNotExist:
                return qs.none()
        return qs

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.company_profile)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """UC-06: Business finalises and submits the application."""
        if request.user.role != "BUSINESS":
            return Response(
                {"detail": "Only business users can submit applications."},
                status=status.HTTP_403_FORBIDDEN,
            )
        application = self.get_object()
        if application.status != "DRAFT":
            return Response(
                {"error": "Only DRAFT applications can be submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        application.status       = "SUBMITTED"
        application.submitted_at = timezone.now()
        application.save()
        return Response(TenderApplicationSerializer(application).data)

    @action(detail=True, methods=["post"])
    def evaluate(self, request, pk=None):
        """UC-07: Admin scores and approves/rejects the application."""
        if request.user.role != "ADMIN":
            return Response(
                {"detail": "Only admins can evaluate applications."},
                status=status.HTTP_403_FORBIDDEN,
            )
        application = self.get_object()
        serializer  = ApplicationEvaluateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        act    = serializer.validated_data["action"]
        score  = serializer.validated_data.get("admin_score")
        reason = serializer.validated_data.get("rejection_reason", "")

        if act == "shortlist":
            application.status = "SHORTLISTED"
        elif act == "approve":
            application.status = "APPROVED"
            Project.objects.filter(pk=application.project.pk).update(
                winning_business=application.business,
                status="EXECUTION",
            )
        elif act == "reject":
            application.status       = "REJECTED"
            application.rejection_reason = reason

        if score is not None:
            application.admin_score = score
        application.evaluated_by = request.user
        application.save()

        return Response(TenderApplicationSerializer(application).data)


# ─────────────────────────────────────────────────────────────────
# UC-08, UC-09: COMPLIANCE EVIDENCE
# ─────────────────────────────────────────────────────────────────

class ComplianceEvidenceViewSet(viewsets.ModelViewSet):
    """
    UC-08: Upload geotagged photo evidence.
    UC-09: Upload legal documents.
    GPS metadata extracted automatically from photo EXIF.
    """
    queryset           = ComplianceEvidence.objects.select_related(
                             "milestone", "uploaded_by"
                         ).all()
    parser_classes     = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return ComplianceEvidenceSerializer

    def perform_create(self, serializer):
        file_obj = self.request.FILES.get("file")
        category = self.request.data.get("category", "")

        gps_lat = gps_lon = captured_at = None
        gps_validated = False

        # UC-08: Extract GPS from photo EXIF (FR_43)
        if category == "PHOTO" and file_obj:
            gps_lat, gps_lon, captured_at = _extract_gps(file_obj)
            file_obj.seek(0)

            milestone_id = self.request.data.get("milestone")
            if milestone_id and gps_lat is not None:
                try:
                    ms = EcoMilestone.objects.select_related("project").get(pk=milestone_id)
                    gps_validated = _validate_gps_against_project(
                        gps_lat, gps_lon, ms.project
                    )
                except EcoMilestone.DoesNotExist:
                    pass

        evidence = serializer.save(
            uploaded_by   = self.request.user,
            gps_latitude  = gps_lat,
            gps_longitude = gps_lon,
            captured_at   = captured_at,
            gps_validated = gps_validated,
        )

        # Move milestone to SUBMITTED after evidence upload
        milestone = evidence.milestone
        if milestone.status == EcoMilestone.MilestoneStatus.PENDING:
            milestone.status = EcoMilestone.MilestoneStatus.SUBMITTED
            milestone.save()


# ─────────────────────────────────────────────────────────────────
# UC-10: CARBON DATA
# ─────────────────────────────────────────────────────────────────

class CarbonDataViewSet(viewsets.ModelViewSet):
    """
    UC-10: Input Carbon Data.
    CO2 calculated automatically via pre_save signal.
    """
    queryset           = CarbonData.objects.select_related("project", "submitted_by").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return CarbonDataSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == "BUSINESS":
            return qs.filter(submitted_by=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


# ─────────────────────────────────────────────────────────────────
# UC-13, UC-14: EXTENSION REQUEST
# ─────────────────────────────────────────────────────────────────

class ExtensionRequestViewSet(viewsets.ModelViewSet):
    """
    UC-13: Business requests deadline extension.
    UC-14: Admin approves or rejects.
    Signal in signals.py updates milestone deadline when approved.
    """
    queryset       = ExtensionRequest.objects.select_related(
                         "milestone", "requested_by", "reviewed_by"
                     ).all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        return ExtensionRequestSerializer

    def get_permissions(self):
        if self.action == "review":
            return [IsAdmin()]
        return [IsBusiness()]

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        """UC-14: Admin approves or rejects — signal updates milestone deadline."""
        if request.user.role != "ADMIN":
            return Response(
                {"detail": "Only admins can review extension requests."},
                status=status.HTTP_403_FORBIDDEN,
            )
        ext_request = self.get_object()
        serializer  = ExtensionReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        act     = serializer.validated_data["action"]
        comment = serializer.validated_data.get("admin_comment", "")

        ext_request.status        = "APPROVED" if act == "approve" else "REJECTED"
        ext_request.admin_comment = comment
        ext_request.reviewed_by   = request.user
        ext_request.save()  # triggers signal in signals.py

        return Response(ExtensionRequestSerializer(ext_request).data)


# ─────────────────────────────────────────────────────────────────
# UC-16: DISCREPANCY REPORT
# ─────────────────────────────────────────────────────────────────

class DiscrepancyReportViewSet(viewsets.ModelViewSet):
    """
    UC-16: Journalist/Public submits whistleblowing report.
    Admin reviews and responds.
    Anonymous submission allowed without login.
    """
    queryset       = DiscrepancyReport.objects.select_related(
                         "project", "reported_by", "reviewed_by"
                     ).all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        return DiscrepancyReportSerializer

    def get_permissions(self):
        if self.action == "respond":
            return [IsAdmin()]
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        is_anon = serializer.validated_data.get("is_anonymous", False)
        user    = self.request.user if self.request.user.is_authenticated else None
        serializer.save(reported_by=None if is_anon else user)
        # Signal sets project.has_red_flag = True

    @action(detail=True, methods=["post"])
    def respond(self, request, pk=None):
        """Admin responds to a discrepancy report."""
        if request.user.role != "ADMIN":
            return Response(
                {"detail": "Only admins can respond to reports."},
                status=status.HTTP_403_FORBIDDEN,
            )
        report     = self.get_object()
        serializer = ReportRespondSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report.status         = serializer.validated_data["status"]
        report.admin_response = serializer.validated_data["admin_response"]
        report.reviewed_by    = request.user
        report.save()

        return Response(DiscrepancyReportSerializer(report).data)


# ─────────────────────────────────────────────────────────────────
# UC-17: PROJECT FOLLOW
# ─────────────────────────────────────────────────────────────────

class ProjectFollowViewSet(viewsets.ModelViewSet):
    """
    UC-17: Follow Project Updates.
    GET    /api/follows/       — list my subscriptions
    POST   /api/follows/       — follow a project
    DELETE /api/follows/{id}/  — unfollow
    """
    queryset           = ProjectFollow.objects.select_related("user", "project").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return ProjectFollowSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ─────────────────────────────────────────────────────────────────
# AUDIT LOG  (FR_10, FR_38) — read only, Admin only
# ─────────────────────────────────────────────────────────────────

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    FR_38: Digital Audit Trail — Admin read only.
    GET /api/audit/                          — paginated log
    GET /api/audit/?model_name=EcoMilestone  — filter by model
    """
    queryset           = AuditLog.objects.select_related("user").all()
    permission_classes = [IsAdmin]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ["action", "model_name", "user__username"]
    ordering_fields    = ["timestamp"]

    def get_serializer_class(self):
        return AuditLogSerializer

    def get_queryset(self):
        qs         = super().get_queryset()
        model_name = self.request.query_params.get("model_name")
        if model_name:
            qs = qs.filter(model_name=model_name)
        return qs
