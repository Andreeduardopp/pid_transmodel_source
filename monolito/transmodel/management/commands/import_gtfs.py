from django.core.management.base import BaseCommand, CommandError

from pid_transit import GtfsImporter, TransitDataset

from transmodel.import_service import GtfsReverseBridge


class Command(BaseCommand):
    help = "Import a GTFS zip file into Django models (Parada, RotaFixa, RotaParada)"

    def add_arguments(self, parser):
        parser.add_argument("file", help="Path to the GTFS .zip file")
        parser.add_argument(
            "--empresa-id",
            type=int,
            required=True,
            help="ID of the EmpresaParceira to assign imported routes to",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        empresa_id = options["empresa_id"]

        self.stdout.write(f"Importing GTFS from: {file_path}")
        self.stdout.write(f"Target empresa_id: {empresa_id}")

        dataset = TransitDataset(":memory:")
        try:
            GtfsImporter().import_to_db(dataset.db, file_path)
        except Exception as e:
            raise CommandError(f"Failed to parse GTFS file: {e}")

        bridge = GtfsReverseBridge(empresa_id=empresa_id)
        report = bridge.import_from_dataset(dataset)

        if report.errors:
            for err in report.errors:
                self.stderr.write(self.style.ERROR(f"  ERROR: {err}"))
            raise CommandError("Import failed with errors")

        self.stdout.write(self.style.SUCCESS(
            f"Import complete: {report.paradas_created} stops, "
            f"{report.rotas_created} routes, "
            f"{report.rota_paradas_created} route-stop links"
        ))

        if report.warnings:
            self.stdout.write(self.style.WARNING(f"\n  Warnings ({len(report.warnings)}):"))
            for w in report.warnings:
                self.stdout.write(self.style.WARNING(f"    - {w}"))
