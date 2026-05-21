from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import EmployeeProfile, Team
from .serializers import EmployeeSerializer, TeamSerializer

User = get_user_model()


class EmployeeViewSet(ModelViewSet):
    queryset = EmployeeProfile.objects.select_related("user", "team", "manager").all().order_by("-id")
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "emp_id"

    def get_queryset(self):
        qs = super().get_queryset()
        emp_id = self.request.query_params.get("emp_id")
        user_id = self.request.query_params.get("user_id")
        team = self.request.query_params.get("team")

        if emp_id:
            qs = qs.filter(emp_id=emp_id)
        if user_id:
            qs = qs.filter(user__id=user_id)
        if team:
            qs = qs.filter(team__id=team)

        return qs


class TeamViewSet(ModelViewSet):
    queryset = Team.objects.all().order_by("name")
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
