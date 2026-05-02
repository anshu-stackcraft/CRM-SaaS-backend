from django.contrib.auth import get_user_model
from clients.models import Client
from deals.models import Deal
from leads.models import Lead
from tasks.models import Task
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .permissions import IsTechnicalOrSuperAdmin
from .permissions import IsSuperAdmin
from .serializers import ProfileSerializer, UserSerializer

User = get_user_model()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response(ProfileSerializer(request.user).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_theme_preference(request):
    theme = request.data.get("theme_preference")
    if theme not in ["light", "dark"]:
        return Response(
            {"detail": "theme_preference must be light or dark."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    request.user.theme_preference = theme
    request.user.save(update_fields=["theme_preference", "updated_at"])
    return Response(ProfileSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register(request):
    requester = request.user
    payload = request.data.copy()
    role = payload.get("role", "employee")

    if requester.role == "super_admin" and role not in ["technical_admin", "employee"]:
        return Response(
            {"detail": "Super admin can create only technical admin or employee."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if requester.role == "technical_admin" and role != "employee":
        return Response(
            {"detail": "Technical admin can create only employee accounts."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if requester.role not in ["super_admin", "technical_admin"]:
        return Response(
            {"detail": "You are not allowed to register users."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = UserSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    return Response(
        {"message": "User created successfully", "user": ProfileSerializer(user).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def setup_super_admin(request):
    if User.objects.filter(role="super_admin").exists():
        return Response(
            {"detail": "Super admin already exists. Use authenticated register flow."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payload = request.data.copy()
    payload["role"] = "super_admin"
    serializer = UserSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(
        {"message": "Super admin created successfully", "user": ProfileSerializer(user).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    user = request.user
    if user.role == "employee":
        users_count = 0
        leads_count = Lead.objects.filter(assigned_to=user).count()
        tasks_count = Task.objects.filter(assigned_to=user).count()
    else:
        users_count = User.objects.count()
        leads_count = Lead.objects.count()
        tasks_count = Task.objects.count()

    return Response(
        {
            "users": users_count,
            "clients": Client.objects.count(),
            "leads": leads_count,
            "deals": Deal.objects.count(),
            "tasks": tasks_count,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_analytics(request):
    try:
        import pandas as pd
    except ModuleNotFoundError:
        return Response(
            {"detail": "pandas is required for analytics. Install it with: pip install pandas"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    clients_qs = Client.objects.values("id", "action", "payment", "created_at", "country")
    leads_qs = Lead.objects.values("id", "status", "created_at")
    deals_qs = Deal.objects.values("id", "amount", "status", "created_at")
    users_qs = User.objects.values("id", "role", "created_at")

    clients_df = pd.DataFrame(list(clients_qs))
    leads_df = pd.DataFrame(list(leads_qs))
    deals_df = pd.DataFrame(list(deals_qs))
    users_df = pd.DataFrame(list(users_qs))

    action_distribution = []
    if not clients_df.empty:
        action_distribution = (
            clients_df["action"].fillna("unknown").value_counts().reset_index().rename(
                columns={"index": "label", "action": "value"}
            ).to_dict(orient="records")
        )

    country_distribution = []
    if not clients_df.empty:
        country_distribution = (
            clients_df["country"].fillna("unknown").value_counts().head(8).reset_index().rename(
                columns={"index": "label", "country": "value"}
            ).to_dict(orient="records")
        )

    lead_status_distribution = []
    if not leads_df.empty:
        lead_status_distribution = (
            leads_df["status"].fillna("unknown").value_counts().reset_index().rename(
                columns={"index": "label", "status": "value"}
            ).to_dict(orient="records")
        )

    role_distribution = []
    if not users_df.empty:
        role_distribution = (
            users_df["role"].fillna("unknown").value_counts().reset_index().rename(
                columns={"index": "label", "role": "value"}
            ).to_dict(orient="records")
        )

    revenue_by_month = []
    if not deals_df.empty:
        deals_df["created_at"] = pd.to_datetime(deals_df["created_at"], errors="coerce")
        deals_df["month"] = deals_df["created_at"].dt.to_period("M").astype(str)
        deals_df["amount"] = pd.to_numeric(deals_df["amount"], errors="coerce").fillna(0)
        revenue_by_month = (
            deals_df.groupby("month", as_index=False)["amount"].sum().rename(
                columns={"month": "label", "amount": "value"}
            ).sort_values("label").to_dict(orient="records")
        )

    return Response(
        {
            "kpis": {
                "total_users": User.objects.count(),
                "total_clients": Client.objects.count(),
                "total_leads": Lead.objects.count(),
                "total_deals": Deal.objects.count(),
                "total_tasks": Task.objects.count(),
            },
            "charts": {
                "action_distribution": action_distribution,
                "country_distribution": country_distribution,
                "lead_status_distribution": lead_status_distribution,
                "role_distribution": role_distribution,
                "revenue_by_month": revenue_by_month,
            },
        }
    )


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsTechnicalOrSuperAdmin]

    def get_permissions(self):
        return [IsAuthenticated(), IsTechnicalOrSuperAdmin()]

    def get_queryset(self):
        requester = self.request.user
        if not requester.is_authenticated:
            return User.objects.filter(role="employee").order_by("-id")
        if requester.role == "super_admin":
            return User.objects.all().order_by("-id")
        return User.objects.filter(role="employee").order_by("-id")

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use /api/users/register/ endpoint for user creation."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
