from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.conf.urls.static import static


def health(_request):
    return JsonResponse({"status": "ok", "service": "DegitalStepIn CRM API"})


# 👇 ADD THIS
def home(request):
    return HttpResponse("🚀 Django CRM Backend Running")


urlpatterns = [
    path('', home),  # 👈 root fix

    path('admin/', admin.site.urls),
    path('api/health/', health),

    path('api/users/', include('users.urls')),
    path('api/leads/', include('leads.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/deals/', include('deals.urls')),
    path('api/tasks/', include('tasks.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)