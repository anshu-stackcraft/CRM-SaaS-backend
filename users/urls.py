from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserViewSet,
    dashboard_summary,
    login,
    profile,
    register,
    setup_super_admin,
    super_admin_analytics,
    super_admin_login,
    update_theme_preference,
    mark_attendance,
    attendance_history,
)

router = DefaultRouter()
router.register("", UserViewSet, basename="users")

urlpatterns = [
    path("login/", login, name="login"),
    path("super-admin-login/", super_admin_login, name="super_admin_login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", profile, name="profile"),
    path("dashboard-summary/", dashboard_summary, name="dashboard_summary"),
    path("attendance/", mark_attendance, name="mark_attendance"),
    path("attendance-history/", attendance_history, name="attendance_history"),
    path("theme-preference/", update_theme_preference, name="theme_preference"),
    path("super-admin-analytics/", super_admin_analytics, name="super_admin_analytics"),
    path("register/", register, name="register"),
    path("setup-super-admin/", setup_super_admin, name="setup_super_admin"),
]

urlpatterns += router.urls
