from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from clients.models import Client
from deals.models import Deal
from leads.models import Lead
from tasks.models import Task

from .permissions import IsSuperAdmin, IsTechnicalOrSuperAdmin
from .serializers import ProfileSerializer, UserSerializer

User = get_user_model()


def _authenticate_with_username_or_email(identifier, password):
    if not identifier or not password:
        return None

    login_username = identifier
    if "@" in identifier:
        matched_user = User.objects.filter(email__iexact=identifier).first()
        if matched_user:
            login_username = matched_user.username

    return authenticate(username=login_username, password=password)


def _token_payload_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": ProfileSerializer(user).data,
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    identifier = request.data.get("username") or request.data.get("email")
    password = request.data.get("password")
    login_as = request.data.get("login_as")

    user = _authenticate_with_username_or_email(identifier, password)
    if not user:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    if login_as and user.role != login_as:
        return Response(
            {"error": f"Access denied for selected role: {login_as}"},
            status=status.HTTP_403_FORBIDDEN,
        )

    return Response(_token_payload_for_user(user), status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def super_admin_login(request):
    identifier = request.data.get("username") or request.data.get("email")
    password = request.data.get("password")

    user = _authenticate_with_username_or_email(identifier, password)
    if not user:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    if user.role != "super_admin":
        return Response(
            {"error": "Access denied. Only Super Admin allowed."},
            status=status.HTTP_403_FORBIDDEN,
        )

    return Response(_token_payload_for_user(user), status=status.HTTP_200_OK)


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

    if requester.role == "super_admin":
        if role not in ["technical_admin", "employee"]:
            return Response(
                {"detail": "Super admin can create only technical admin or employee."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    elif requester.role == "technical_admin":
        if role != "employee":
            return Response(
                {"detail": "Technical admin can create only employee accounts."},
                status=status.HTTP_403_FORBIDDEN,
            )
    else:
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
            {"detail": "Super admin already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payload = request.data.copy()
    payload["role"] = "super_admin"

    serializer = UserSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    return Response(
        {
            "message": "Super admin created successfully",
            "user": ProfileSerializer(user).data,
        },
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
        deals_count = Deal.objects.filter(assigned_to=user).count() if hasattr(Deal, "assigned_to") else Deal.objects.count()
    else:
        users_count = User.objects.count()
        leads_count = Lead.objects.count()
        tasks_count = Task.objects.count()
        deals_count = Deal.objects.count()

    return Response(
        {
            "users": users_count,
            "clients": Client.objects.count(),
            "leads": leads_count,
            "deals": deals_count,
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
            {"detail": "Install pandas: pip install pandas"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    clients_df = pd.DataFrame(
        list(Client.objects.values("action", "payment", "created_at", "country"))
    )
    leads_df = pd.DataFrame(list(Lead.objects.values("status")))
    deals_df = pd.DataFrame(list(Deal.objects.values("amount", "created_at")))
    users_df = pd.DataFrame(list(User.objects.values("role")))

    def distribution(df, col):
        if df.empty or col not in df.columns:
            return []
        counts = df[col].fillna("unknown").astype(str).value_counts()
        return [{"label": key, "value": int(value)} for key, value in counts.items()]

    revenue_by_month = []
    if not deals_df.empty and {"created_at", "amount"}.issubset(deals_df.columns):
        deals_df["created_at"] = pd.to_datetime(deals_df["created_at"], errors="coerce")
        deals_df["amount"] = pd.to_numeric(deals_df["amount"], errors="coerce").fillna(0)

        valid_deals = deals_df.dropna(subset=["created_at"])
        if not valid_deals.empty:
            valid_deals["month"] = valid_deals["created_at"].dt.strftime("%Y-%m")
            monthly = valid_deals.groupby("month")["amount"].sum().sort_index()
            revenue_by_month = [
                {"label": month, "value": float(amount)}
                for month, amount in monthly.items()
            ]

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
                "action_distribution": distribution(clients_df, "action"),
                "country_distribution": distribution(clients_df, "country"),
                "lead_status_distribution": distribution(leads_df, "status"),
                "user_role_distribution": distribution(users_df, "role"),
                "revenue_by_month": revenue_by_month,
            },
        }
    )


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsTechnicalOrSuperAdmin]

    def get_queryset(self):
        requester = self.request.user

        if requester.role == "super_admin":
            return User.objects.all().order_by("-id")

        return User.objects.filter(role="employee").order_by("-id")

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use /api/users/register/ endpoint."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
