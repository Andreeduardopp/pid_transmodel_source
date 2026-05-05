from dataclasses import dataclass, field
from typing import List

from django.contrib.gis.geos import Point
from django.db import transaction

from empresa.models import EmpresaParceira
from logistica.models import Parada, RotaFixa, RotaParada
from pid_transit import TransitDataset


@dataclass
class ImportReport:
    paradas_created: int = 0
    rotas_created: int = 0
    rota_paradas_created: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


DAY_PATTERN_MAP = {
    (True, True, True, True, True, False, False): "SEG_SEX",
    (True, True, True, True, True, True, False): "SEG_SAB",
    (True, True, True, True, True, True, True): "TODO_DIA",
    (False, False, False, False, False, True, True): "FIM_SEMANA",
}


class GtfsReverseBridge:
    def __init__(self, empresa_id: int):
        self.empresa_id = empresa_id

    def import_from_dataset(self, dataset: TransitDataset) -> ImportReport:
        report = ImportReport()

        empresa = EmpresaParceira.objects.filter(id=self.empresa_id).first()
        if not empresa:
            report.errors.append(f"EmpresaParceira id={self.empresa_id} not found")
            return report

        with transaction.atomic():
            stop_map = self._import_stops(dataset, report)
            self._import_routes(dataset, report, stop_map)

        return report

    def _import_stops(self, dataset: TransitDataset, report: ImportReport) -> dict:
        stop_map = {}
        for ssp in dataset.scheduled_stop_points.get_all():
            parada = Parada.objects.create(
                endereco=ssp.name,
                localizacao=Point(ssp.lon, ssp.lat, srid=4326),
            )
            stop_map[ssp.id] = parada
            report.paradas_created += 1
        return stop_map

    def _import_routes(self, dataset: TransitDataset, report: ImportReport, stop_map: dict):
        journey_pattern_stops = {}
        for pijp in dataset.points_in_journey_pattern.get_all():
            journey_pattern_stops.setdefault(pijp.journey_pattern_id, []).append(pijp)

        for jp_id, points in journey_pattern_stops.items():
            points.sort(key=lambda p: p.order)

        day_types_by_id = {dt.id: dt for dt in dataset.day_types.get_all()}

        for sj in dataset.service_journeys.get_all():
            jp_id = sj.journey_pattern_id
            if not jp_id or jp_id not in journey_pattern_stops:
                report.warnings.append(f"ServiceJourney {sj.id}: no journey pattern stops, skipped")
                continue

            points = journey_pattern_stops[jp_id]
            if len(points) < 2:
                report.warnings.append(f"ServiceJourney {sj.id}: fewer than 2 stops, skipped")
                continue

            first_stop = stop_map.get(points[0].stop_point_id)
            last_stop = stop_map.get(points[-1].stop_point_id)
            if not first_stop or not last_stop:
                report.warnings.append(f"ServiceJourney {sj.id}: stop mapping missing, skipped")
                continue

            dias = self._match_day_pattern(day_types_by_id.get(sj.day_type_id))

            rota = RotaFixa.objects.create(
                origem_nome=first_stop.endereco,
                destino_nome=last_stop.endereco,
                origem_localizacao=first_stop.localizacao,
                destino_localizacao=last_stop.localizacao,
                empresa_id=self.empresa_id,
                horario_partida=sj.departure_time,
                dias_da_semana=dias,
            )
            report.rotas_created += 1

            for pt in points:
                parada = stop_map.get(pt.stop_point_id)
                if not parada:
                    continue
                RotaParada.objects.create(
                    parada=parada,
                    rota_fixa=rota,
                    ordem=pt.order + 1,
                )
                report.rota_paradas_created += 1

    def _match_day_pattern(self, dt) -> str:
        if dt is None:
            return "TODO_DIA"
        flags = (dt.monday, dt.tuesday, dt.wednesday, dt.thursday, dt.friday, dt.saturday, dt.sunday)
        if flags in DAY_PATTERN_MAP:
            return DAY_PATTERN_MAP[flags]
        if all(flags[:5]) and any(flags[5:]):
            return "SEG_SAB" if flags[5] else "SEG_SEX"
        if any(flags[5:]) and not any(flags[:5]):
            return "FIM_SEMANA"
        return "TODO_DIA"
