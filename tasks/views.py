from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from users.permissions import IsAuthenticatedAndReadOnlyForEmployee

from .models import Task
from .serializers import TaskSerializer

User = get_user_model()


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedAndReadOnlyForEmployee]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.all().order_by("-id")
        if user.role == "employee":
            return Task.objects.filter(assigned_to=user).order_by("-id")
        return Task.objects.all().order_by("-id")

    def perform_create(self, serializer):
        user = self.request.user
        assigned_to_id = self.request.data.get("assigned_to")
        if user.role in ["super_admin", "technical_admin"] and assigned_to_id:
            assignee = User.objects.filter(id=assigned_to_id).first()
            serializer.save(assigned_to=assignee or user)
        else:
            serializer.save(assigned_to=user)
