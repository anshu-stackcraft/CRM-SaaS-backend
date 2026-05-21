from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.conf.urls.static import static


# ✅ Home (root) – show links instead of text
def home(request):
    # A simple HTML response with links to all API endpoints and admin panel
    return HttpResponse("""
        <h2>CRM Backend API</h2>
        <p>Available Endpoints:</p>
        <ul>
            <li><a href="/admin/">Admin Panel</a></li>
            <li><a href="/api/health/">Health Check</a></li>
            <li><a href="/api/users/">Users API</a></li>
            <li><a href="/api/leads/">Leads API</a></li>
            <li><a href="/api/clients/">Clients API</a></li>
            <li><a href="/api/deals/">Deals API</a></li>
            <li><a href="/api/tasks/">Tasks API</a></li>
        </ul>
    """)


# ✅ Health check
def health(request):
    return JsonResponse({
        "status": "ok",
        "service": "DigitalStepIn CRM API"
    })


# ✅ URL routes
urlpatterns = [
    path('', home),

    path('admin/', admin.site.urls),

    path('api/health/', health),

    path('api/users/', include('users.urls')),
    path('api/leads/', include('leads.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/deals/', include('deals.urls')),
    path('api/tasks/', include('tasks.urls')),
    path('api/emp/', include('emp.urls')),
]


# ✅ Media (dev only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)