import uuid

from django.db import models


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f'Customer {self.id}'


class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    def __str__(self):
        return f'Device {self.id}'


class Reading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.PROTECT)
    timestamp = models.DateTimeField()
    reading = models.FloatField()

    def __str__(self):
        return f'Reading {self.id}'
