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
        queryset = Task.objects.all().order_by("-id")
        assigned_to = self.request.query_params.get("assigned_to")

        if not user.is_authenticated:
            return queryset

        if user.role == "employee":
            queryset = queryset.filter(assigned_to=user)
        elif assigned_to:
            queryset = queryset.filter(assigned_to__id=assigned_to)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        assigned_to_id = self.request.data.get("assigned_to")
        if user.role in ["super_admin", "technical_admin"] and assigned_to_id:
            assignee = User.objects.filter(id=assigned_to_id, role="employee").first()
            if not assignee:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"assigned_to": "A valid employee assignee is required."})
            serializer.save(assigned_to=assignee)
        else:
            serializer.save(assigned_to=user)

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.instance
        assigned_to_id = self.request.data.get("assigned_to")

        # Admins can reassign tasks to valid employees
        if user.role in ["super_admin", "technical_admin"] and assigned_to_id:
            assignee = User.objects.filter(id=assigned_to_id, role="employee").first()
            if not assignee:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"assigned_to": "A valid employee assignee is required."})
            serializer.save(assigned_to=assignee)
            return

        # Employees may only update their own tasks and cannot reassign
        if user.role == "employee":
            if instance.assigned_to != user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied({"detail": "You may not modify tasks not assigned to you."})

            # Prevent employees from changing the assignee
            if assigned_to_id and str(assigned_to_id) != str(user.id):
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"assigned_to": "You cannot change task assignee."})

            serializer.save()
            return

        # Default fallback for other cases
        serializer.save()
