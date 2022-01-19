from django.db.utils import IntegrityError

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Customer, Device, Reading


class AddReadingsSerializer(serializers.ListSerializer):

    def _create(self, validated_data):
        for d in validated_data:
            Customer.objects.get_or_create(
                id=d['customer_id'],
            )
            Device.objects.get_or_create(
                id=d['device_id'],
                customer_id=d['customer_id'],
            )
            Reading.objects.create(
                device_id=d['device_id'],
                timestamp=d['timestamp'],
                reading=d['reading'],
            )

        return validated_data

    def create(self, validated_data):
        try:
            return self._create(validated_data)
        except IntegrityError:
            raise ValidationError('Invalid customer or device')


class AddReadingSerializer(serializers.Serializer):

    customer_id = serializers.UUIDField()
    device_id = serializers.UUIDField()
    timestamp = serializers.DateTimeField()
    reading = serializers.FloatField()

    class Meta:
        list_serializer_class = AddReadingsSerializer
