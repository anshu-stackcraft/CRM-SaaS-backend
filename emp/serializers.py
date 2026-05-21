from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EmployeeProfile, Team

User = get_user_model()


class TeamSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(source="members.count", read_only=True)

    class Meta:
        model = Team
        fields = ["id", "name", "description", "members_count"]


class EmployeeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="manager", allow_null=True, required=False)
    team_id = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all(), source="team", allow_null=True, required=False)

    class Meta:
        model = EmployeeProfile
        fields = [
            "id",
            "emp_id",
            "user_id",
            "username",
            "full_name",
            "email",
            "position",
            "phone",
            "address",
            "manager_id",
            "team_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "emp_id": {"required": False, "allow_blank": True},
        }
