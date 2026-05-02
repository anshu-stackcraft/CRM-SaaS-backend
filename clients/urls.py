from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ClientViewSet, import_excel_clients, list_imported_files

router = DefaultRouter()
router.register('', ClientViewSet)

urlpatterns = router.urls
urlpatterns += [
    path("import-excel/", import_excel_clients, name="import_excel_clients"),
    path("import-files/", list_imported_files, name="import_files"),
]
