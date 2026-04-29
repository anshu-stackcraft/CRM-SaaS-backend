from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health(_request):
    return JsonResponse({"status": "ok", "service": "DegitalStepIn CRM API"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health),

    path('api/users/', include('users.urls')),
    path('api/leads/', include('leads.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/deals/', include('deals.urls')),
    path('api/tasks/', include('tasks.urls')),
]
