from django.contrib.auth import get_user_model
from clients.models import Client
from deals.models import Deal
from leads.models import Lead
from tasks.models import Task
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .permissions import IsTechnicalOrSuperAdmin
from .serializers import ProfileSerializer, UserSerializer

User = get_user_model()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
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
            {"detail": "Use /api/users/register/ endpoint for user creation."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
