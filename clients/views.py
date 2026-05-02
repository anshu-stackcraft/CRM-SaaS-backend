from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsAuthenticatedAndReadOnlyForEmployee

from .models import Client, ClientImportFile
from .serializers import ClientSerializer


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all().order_by("-id")
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticatedAndReadOnlyForEmployee]


@api_view(["POST"])
@permission_classes([IsAuthenticatedAndReadOnlyForEmployee])
def import_excel_clients(request):
    if request.user.role not in ["super_admin", "technical_admin"]:
        return Response({"detail": "Only admin users can import excel."}, status=status.HTTP_403_FORBIDDEN)

    if "file" not in request.FILES:
        return Response({"detail": "Excel file is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        import pandas as pd
    except ModuleNotFoundError:
        return Response(
            {"detail": "pandas is required. Install it with: pip install pandas"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    excel_file = request.FILES["file"]
    file_record = ClientImportFile.objects.create(
        file=excel_file,
        original_name=excel_file.name,
        uploaded_by=request.user,
    )
    try:
        df = pd.read_excel(file_record.file.path)
    except Exception:
        file_record.delete()
        return Response({"detail": "Invalid excel file."}, status=status.HTTP_400_BAD_REQUEST)

    if df.empty:
        return Response({"detail": "Excel file has no rows."}, status=status.HTTP_400_BAD_REQUEST)

    normalized = {str(c).strip().lower(): c for c in df.columns}

    def col(*options):
        for opt in options:
            if opt in normalized:
                return normalized[opt]
        return None

    name_col = col("name", "client_name")
    mac_col = col("mac_address", "mac", "mac address")
    phone_col = col("phone", "mobile")
    country_col = col("country")
    comments_col = col("comments", "comment", "notes")
    action_col = col("action")
    payment_col = col("payment", "amount")
    active_col = col("is_active", "active")
    follow_up_col = col("follow_up_time", "follow up time", "followup_time")

    if not name_col or not mac_col or not phone_col:
        return Response(
            {"detail": "Required columns: name, mac_address, phone"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    created = 0
    updated = 0
    preview = []
    allowed_actions = {"call", "follow_up", "closed"}
    for _, row in df.iterrows():
        name = str(row.get(name_col, "")).strip()
        mac_address = str(row.get(mac_col, "")).strip()
        phone = str(row.get(phone_col, "")).strip()
        if not name or not mac_address or not phone:
            continue

        raw_action = str(row.get(action_col, "")).strip() if action_col else ""
        normalized_action = raw_action.lower()
        defaults = {
            "name": name,
            "phone": phone,
            "country": str(row.get(country_col, "India")).strip() if country_col else "India",
            "comments": str(row.get(comments_col, "")).strip() if comments_col else "",
            "action": normalized_action if normalized_action in allowed_actions else "",
        }
        if payment_col:
            try:
                defaults["payment"] = float(row.get(payment_col, 0) or 0)
            except Exception:
                defaults["payment"] = 0
        if active_col:
            raw = str(row.get(active_col, "false")).strip().lower()
            defaults["is_active"] = raw in ["true", "1", "yes", "y"]
        if follow_up_col:
            follow_up_val = row.get(follow_up_col)
            if pd.notna(follow_up_val):
                parsed_follow_up = pd.to_datetime(follow_up_val, errors="coerce")
                if pd.notna(parsed_follow_up):
                    defaults["follow_up_time"] = parsed_follow_up.to_pydatetime()

        obj, was_created = Client.objects.update_or_create(
            mac_address=mac_address,
            defaults=defaults,
        )
        if was_created:
            created += 1
        else:
            updated += 1

        if len(preview) < 50:
            preview.append(
                {
                    "id": obj.id,
                    "name": obj.name,
                    "mac_address": obj.mac_address,
                    "phone": obj.phone,
                    "country": obj.country,
                    "payment": str(obj.payment),
                    "is_active": obj.is_active,
                    "action": obj.action,
                }
            )

    file_record.created_count = created
    file_record.updated_count = updated
    file_record.total_rows = int(len(df.index))
    file_record.save(update_fields=["created_count", "updated_count", "total_rows"])

    return Response(
        {
            "created": created,
            "updated": updated,
            "total_rows": int(len(df.index)),
            "preview": preview,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticatedAndReadOnlyForEmployee])
def list_imported_files(request):
    if request.user.role not in ["super_admin", "technical_admin"]:
        return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

    files = ClientImportFile.objects.select_related("uploaded_by")[:30]
    payload = [
        {
            "id": f.id,
            "original_name": f.original_name,
            "file_url": f.file.url if f.file else "",
            "uploaded_by": f.uploaded_by.username,
            "created_count": f.created_count,
            "updated_count": f.updated_count,
            "total_rows": f.total_rows,
            "created_at": f.created_at,
        }
        for f in files
    ]
    return Response(payload)
