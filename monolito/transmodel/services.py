from datetime import date, timedelta

from django.db.models import Prefetch

from empresa.models import EmpresaParceira
from logistica.models import Parada, RotaExtra, RotaFixa, RotaParada
from pid_transit import (
    DayType,
    DirectionType,
    JourneyPattern,
    Line,
    Operator,
    PassingTime,
    PointInJourneyPattern,
    ScheduledStopPoint,
    ServiceJourney,
    TransitDataset,
    TransportMode,
)

DAY_TYPE_FLAGS = {
    "SEG_SEX": {"monday": True, "tuesday": True, "wednesday": True, "thursday": True, "friday": True},
    "SEG_SAB": {"monday": True, "tuesday": True, "wednesday": True, "thursday": True, "friday": True, "saturday": True},
    "TODO_DIA": {"monday": True, "tuesday": True, "wednesday": True, "thursday": True, "friday": True, "saturday": True, "sunday": True},
    "FIM_SEMANA": {"saturday": True, "sunday": True},
}

WEEKDAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class TransmodelBridge:
    def build_dataset(self, db_path: str = ":memory:", start_date=None, end_date=None) -> TransitDataset:
        dataset = TransitDataset(db_path)
        self._load_operators(dataset)
        self._load_stop_points(dataset)
        self._load_day_types(dataset, start_date, end_date)
        self._load_lines(dataset)
        self._load_journey_patterns(dataset)
        self._load_service_journeys(dataset)
        self._load_passing_times(dataset)
        return dataset

    def _load_operators(self, dataset: TransitDataset):
        objs = EmpresaParceira.objects.all()
        dataset.operators.add_many([
            Operator(
                id=f"OP_{obj.id}",
                name=obj.nome,
                timezone="America/Sao_Paulo",
            )
            for obj in objs
        ])

    def _load_stop_points(self, dataset: TransitDataset):
        objs = Parada.objects.all()
        dataset.scheduled_stop_points.add_many([
            ScheduledStopPoint(
                id=f"SSP_{obj.id}",
                name=obj.endereco,
                lat=obj.localizacao.y,
                lon=obj.localizacao.x,
            )
            for obj in objs
            if obj.localizacao is not None
        ])

    def _load_day_types(self, dataset: TransitDataset, start_date=None, end_date=None):
        used = RotaFixa.objects.values_list("dias_da_semana", flat=True).distinct()
        sd = (start_date or date.today()).isoformat()
        ed = (end_date or date.today() + timedelta(days=365)).isoformat()
        day_types = [
            DayType(id=f"DT_{pattern}", start_date=sd, end_date=ed, **DAY_TYPE_FLAGS[pattern])
            for pattern in used
        ]

        for extra in RotaExtra.objects.exclude(status="cancelada"):
            d = extra.data_hora_execucao.date()
            flags = {day: (i == d.weekday()) for i, day in enumerate(WEEKDAY_NAMES)}
            day_types.append(DayType(
                id=f"DT_EXTRA_{extra.id}",
                start_date=d.isoformat(),
                end_date=d.isoformat(),
                **flags,
            ))

        dataset.day_types.add_many(day_types)

    def _load_lines(self, dataset: TransitDataset):
        lines = [
            Line(
                id=f"L_{obj.id}",
                operator_id=f"OP_{obj.empresa_id}",
                name=f"{obj.origem_nome} → {obj.destino_nome}",
                short_name=obj.origem_nome[:10],
                transport_mode=TransportMode.BUS,
            )
            for obj in RotaFixa.objects.all()
        ]

        extra_empresa_ids = (
            RotaExtra.objects.exclude(status="cancelada")
            .values_list("empresa_id", flat=True)
            .distinct()
        )
        for eid in extra_empresa_ids:
            lines.append(Line(
                id=f"L_EXTRA_{eid}",
                operator_id=f"OP_{eid}",
                name="Rotas Extras (ad-hoc)",
                transport_mode=TransportMode.BUS,
            ))

        dataset.lines.add_many(lines)

    def _load_journey_patterns(self, dataset: TransitDataset):
        patterns = []
        points = []
        rotas = RotaFixa.objects.prefetch_related(
            Prefetch("rota_paradas", queryset=RotaParada.objects.order_by("ordem"))
        ).all()
        for rota in rotas:
            patterns.append(JourneyPattern(
                id=f"JP_{rota.id}",
                line_id=f"L_{rota.id}",
                direction=DirectionType.OUTBOUND,
            ))
            for rp in rota.rota_paradas.all():
                points.append(PointInJourneyPattern(
                    journey_pattern_id=f"JP_{rota.id}",
                    stop_point_id=f"SSP_{rp.parada_id}",
                    order=rp.ordem - 1,
                ))
        dataset.journey_patterns.add_many(patterns)
        dataset.points_in_journey_pattern.add_many(points)

    def _load_service_journeys(self, dataset: TransitDataset):
        journeys = []

        for obj in RotaFixa.objects.all():
            journeys.append(ServiceJourney(
                id=f"SJ_FIXA_{obj.id}",
                line_id=f"L_{obj.id}",
                journey_pattern_id=f"JP_{obj.id}",
                day_type_id=f"DT_{obj.dias_da_semana}",
                departure_time=obj.horario_partida.strftime("%H:%M:%S"),
            ))

        for obj in RotaExtra.objects.exclude(status="cancelada"):
            journeys.append(ServiceJourney(
                id=f"SJ_EXTRA_{obj.id}",
                line_id=f"L_EXTRA_{obj.empresa_id}",
                journey_pattern_id=None,
                day_type_id=f"DT_EXTRA_{obj.id}",
                departure_time=obj.data_hora_execucao.strftime("%H:%M:%S"),
            ))

        dataset.service_journeys.add_many(journeys)

    def _load_passing_times(self, dataset: TransitDataset):
        times = []
        rps = (
            RotaParada.objects
            .select_related("rota_fixa", "rota_extra")
            .exclude(rota_extra__status="cancelada")
            .all()
        )
        for rp in rps:
            if rp.rota_fixa_id:
                sj_id = f"SJ_FIXA_{rp.rota_fixa_id}"
            else:
                sj_id = f"SJ_EXTRA_{rp.rota_extra_id}"
            times.append(PassingTime(
                service_journey_id=sj_id,
                stop_point_id=f"SSP_{rp.parada_id}",
                order=rp.ordem - 1,
                arrival_time=None,
                departure_time=None,
            ))
        dataset.passing_times.add_many(times)
