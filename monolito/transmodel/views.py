import os
import tempfile

from django.http import FileResponse, JsonResponse
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pid_transit import GtfsExporter, GtfsImporter, NetexExporter, TransitDataset

from .import_service import GtfsReverseBridge
from .services import TransmodelBridge


def _build_and_validate():
    bridge = TransmodelBridge()
    dataset = bridge.build_dataset(db_path=":memory:")
    report = dataset.validate()
    critical_issues = [
        i for i in report.issues
        if not (i.issue_type == "no_journey_patterns" and i.entity_id.startswith("L_EXTRA_"))
    ]
    return dataset, critical_issues


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_gtfs(request):
    dataset, critical_issues = _build_and_validate()
    if critical_issues:
        return JsonResponse(
            {"errors": [{"entity": i.entity_type, "id": i.entity_id, "message": i.message} for i in critical_issues]},
            status=400,
        )

    tmp_path = tempfile.mktemp(suffix=".zip")
    try:
        GtfsExporter().export_from_db(dataset.db, tmp_path)
        response = FileResponse(
            open(tmp_path, "rb"),
            content_type="application/zip",
            as_attachment=True,
            filename="transporte_gtfs.zip",
        )
        response._resource_closers.append(lambda: os.unlink(tmp_path))
        return response
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_netex(request):
    dataset, critical_issues = _build_and_validate()
    if critical_issues:
        return JsonResponse(
            {"errors": [{"entity": i.entity_type, "id": i.entity_id, "message": i.message} for i in critical_issues]},
            status=400,
        )

    tmp_path = tempfile.mktemp(suffix=".xml")
    try:
        NetexExporter(profile="EPIP").export_from_db(dataset.db, tmp_path)
        response = FileResponse(
            open(tmp_path, "rb"),
            content_type="application/xml; charset=utf-8",
            as_attachment=True,
            filename="transporte_netex.xml",
        )
        response["X-Export-Coverage"] = "full"
        response._resource_closers.append(lambda: os.unlink(tmp_path))
        return response
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def import_gtfs(request):
    file = request.FILES.get("file")
    empresa_id = request.data.get("empresa_id")

    if not file:
        return Response({"error": "No file provided"}, status=400)
    if not empresa_id:
        return Response({"error": "empresa_id is required"}, status=400)

    try:
        empresa_id = int(empresa_id)
    except (TypeError, ValueError):
        return Response({"error": "empresa_id must be an integer"}, status=400)

    tmp_path = tempfile.mktemp(suffix=".zip")
    try:
        with open(tmp_path, "wb") as f:
            for chunk in file.chunks():
                f.write(chunk)

        dataset = TransitDataset(":memory:")
        GtfsImporter().import_to_db(dataset.db, tmp_path)

        bridge = GtfsReverseBridge(empresa_id=empresa_id)
        report = bridge.import_from_dataset(dataset)

        if report.errors:
            return Response({"errors": report.errors, "warnings": report.warnings}, status=400)

        return Response({
            "paradas_created": report.paradas_created,
            "rotas_created": report.rotas_created,
            "rota_paradas_created": report.rota_paradas_created,
            "warnings": report.warnings,
        }, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
