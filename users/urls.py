from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserViewSet, dashboard_summary, profile, register

router = DefaultRouter()
router.register("", UserViewSet, basename="users")

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", profile, name="profile"),
    path("dashboard-summary/", dashboard_summary, name="dashboard_summary"),
    path("register/", register, name="register"),
]

urlpatterns += router.urls
