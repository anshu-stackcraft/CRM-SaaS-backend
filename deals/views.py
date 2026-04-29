from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Deal
from .serializers import DealSerializer


class DealViewSet(ModelViewSet):
    queryset = Deal.objects.all().order_by("-id")
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated]
