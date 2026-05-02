from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserViewSet,
    dashboard_summary,
    profile,
    register,
    setup_super_admin,
    super_admin_analytics,
    update_theme_preference,
)

router = DefaultRouter()
router.register("", UserViewSet, basename="users")

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", profile, name="profile"),
    path("dashboard-summary/", dashboard_summary, name="dashboard_summary"),
    path("theme-preference/", update_theme_preference, name="theme_preference"),
    path("super-admin-analytics/", super_admin_analytics, name="super_admin_analytics"),
    path("register/", register, name="register"),
    path("setup-super-admin/", setup_super_admin, name="setup_super_admin"),
]

urlpatterns += router.urls
