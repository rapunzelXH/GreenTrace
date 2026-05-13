# greentrace/api/permissions.py
#
# Custom DRF permission classes for role-based access control.
# Used across all ViewSets to restrict actions by user role.

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only Government Administrators can access."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsBusiness(BasePermission):
    """Only Business / Contractor users can access."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "BUSINESS"
        )


class IsJournalist(BasePermission):
    """Only Journalist / Public users can access."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "JOURNALIST"
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Admin can do anything.
    Authenticated users can only read (GET, HEAD, OPTIONS).
    """
    SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in self.SAFE_METHODS:
            return True
        return request.user.role == "ADMIN"


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level: owner of the object or Admin can access.
    Used for TenderApplication, ComplianceEvidence etc.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMIN":
            return True
        # check various owner fields
        owner = (
            getattr(obj, "business", None)
            or getattr(obj, "uploaded_by", None)
            or getattr(obj, "submitted_by", None)
            or getattr(obj, "requested_by", None)
            or getattr(obj, "reported_by", None)
            or getattr(obj, "user", None)
        )
        if owner is None:
            return False
        # owner may be a User or CompanyProfile
        if hasattr(owner, "user"):
            return owner.user == request.user
        return owner == request.user
