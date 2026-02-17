from rest_framework import serializers
from django.db import transaction

from empresa.models import EmpresaParceira, Motorista, Veiculo
from .models import RotaExtra, Parada


class ParadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parada
        fields = ['id', 'endereco', 'ordem', 'referencia']


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

            for parada_data in paradas_data:
                Parada.objects.create(rota=rota, **parada_data)

        return rota

    def update(self, instance: RotaExtra, validated_data: dict) -> RotaExtra:
        paradas_data = validated_data.pop('paradas', None)

        with transaction.atomic():
            # Atualiza campos da rota
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Se paradas foram enviadas, substituímos as existentes (estratégia simples)
            if paradas_data is not None:
                instance.paradas.all().delete()
                for parada_data in paradas_data:
                    Parada.objects.create(rota=instance, **parada_data)

        return instance
