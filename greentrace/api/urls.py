# greentrace/api/urls.py
#
# All API endpoints registered via DRF Router + custom JWT auth routes.

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from .views import (
    RegisterViewSet,
    UserProfileViewSet,
    CompanyProfileViewSet,
    ProjectViewSet,
    EcoMilestoneViewSet,
    TenderApplicationViewSet,
    ComplianceEvidenceViewSet,
    CarbonDataViewSet,
    ExtensionRequestViewSet,
    DiscrepancyReportViewSet,
    ProjectFollowViewSet,
    AuditLogViewSet,
)

router = DefaultRouter()
router.register(r"companies",    CompanyProfileViewSet,    basename="company")
router.register(r"projects",     ProjectViewSet,           basename="project")
router.register(r"milestones",   EcoMilestoneViewSet,      basename="milestone")
router.register(r"applications", TenderApplicationViewSet, basename="application")
router.register(r"evidence",     ComplianceEvidenceViewSet,basename="evidence")
router.register(r"carbon",       CarbonDataViewSet,        basename="carbon")
router.register(r"extensions",   ExtensionRequestViewSet,  basename="extension")
router.register(r"reports",      DiscrepancyReportViewSet, basename="report")
router.register(r"follows",      ProjectFollowViewSet,     basename="follow")
router.register(r"audit",        AuditLogViewSet,          basename="audit")

urlpatterns = [
    # ── JWT Authentication (UC-01, UC-02, UC-35) ─────────────────
    path("auth/register/", RegisterViewSet.as_view({"post": "create"}),   name="register"),
    path("auth/login/",    TokenObtainPairView.as_view(),                  name="token_obtain"),
    path("auth/refresh/",  TokenRefreshView.as_view(),                     name="token_refresh"),
    path("auth/logout/",   TokenBlacklistView.as_view(),                   name="token_blacklist"),

    # ── Own profile  (UC-03) ──────────────────────────────────────
    path("auth/me/",       UserProfileViewSet.as_view({"get": "list", "put": "update"}), name="me"),

    # ── All router-registered endpoints ──────────────────────────
    path("", include(router.urls)),
]
