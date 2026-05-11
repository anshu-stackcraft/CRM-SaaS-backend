from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    ClientViewSet,
    import_excel_clients,
    list_imported_files,
    export_excel_clients,
)

router = DefaultRouter()
router.register('', ClientViewSet)

urlpatterns = [
    path("import-excel/", import_excel_clients, name="import_excel_clients"),
    path("export-excel/", export_excel_clients, name="export_excel_clients"),
    path("export-clients/", export_excel_clients, name="export_clients"),
    path("import-files/", list_imported_files, name="import_files"),
]
urlpatterns += router.urls
