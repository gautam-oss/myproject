from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Auth
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Tenant-scoped modules (added in Phase 2+)
    # path("patients/", include("apps.patients.urls")),
    # path("scheduling/", include("apps.scheduling.urls")),
    # path("billing/", include("apps.billing.urls")),
]
