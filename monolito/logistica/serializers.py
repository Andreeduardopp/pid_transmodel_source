from django.contrib.gis.geos import Point
from django.db import transaction
from pydantic import ValidationError as PydanticValidationError
from rest_framework import serializers

from pid_transit import ScheduledStopPoint

from empresa.models import EmpresaParceira, Motorista, Veiculo
from .models import Parada, RotaExtra, RotaParada


class ParadaSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    ordem = serializers.IntegerField(required=False)

    class Meta:
        model = Parada
        fields = ['id', 'endereco', 'ordem', 'referencia', 'latitude', 'longitude']

    def validate(self, data):
        lat = data.get("latitude")
        lon = data.get("longitude")
        if lat is not None and lon is not None:
            try:
                ScheduledStopPoint(
                    id="validation_probe",
                    name=data.get("endereco", ""),
                    lat=lat,
                    lon=lon,
                )
            except PydanticValidationError as e:
                raise serializers.ValidationError(
                    {"coordinates": [err["msg"] for err in e.errors()]}
                )
            data["localizacao"] = Point(lon, lat, srid=4326)
        return data


class RotaExtraSerializer(serializers.ModelSerializer):
    paradas = ParadaSerializer(many=True, required=False)

    class Meta:
        model = RotaExtra
        fields = [
            'id', 'origem_nome', 'destino_nome', 'empresa', 'veiculo', 'motorista',
            'data_hora_execucao', 'quantidade_passageiros', 'status', 'origem_whatsapp',
            'paradas'
        ]

    def create(self, validated_data: dict) -> RotaExtra:
        paradas_data = validated_data.pop('paradas', [])

        with transaction.atomic():
            rota = RotaExtra.objects.create(**validated_data)

            for i, parada_data in enumerate(paradas_data):
                ordem = parada_data.pop('ordem', i + 1)
                localizacao = parada_data.pop('localizacao', None)
                parada_data.pop('latitude', None)
                parada_data.pop('longitude', None)
                parada = Parada.objects.create(localizacao=localizacao, **parada_data)
                RotaParada.objects.create(
                    parada=parada,
                    rota_extra=rota,
                    ordem=ordem,
                )

        return rota

    def update(self, instance: RotaExtra, validated_data: dict) -> RotaExtra:
        paradas_data = validated_data.pop('paradas', None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if paradas_data is not None:
                RotaParada.objects.filter(rota_extra=instance).delete()
                for i, parada_data in enumerate(paradas_data):
                    ordem = parada_data.pop('ordem', i + 1)
                    localizacao = parada_data.pop('localizacao', None)
                    parada_data.pop('latitude', None)
                    parada_data.pop('longitude', None)
                    parada = Parada.objects.create(localizacao=localizacao, **parada_data)
                    RotaParada.objects.create(
                        parada=parada,
                        rota_extra=instance,
                        ordem=ordem,
                    )

        return instance
