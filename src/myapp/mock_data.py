from datetime import timedelta
from random import random
from uuid import uuid4

from django.utils import timezone

from myapp.models import Customer, Device, Reading

N_CUSTOMERS = 4
N_DEVICES_PER_CUSTOMER = 6
N_READINGS = 200

MOCK_CUSTOMER_DEVICES = {
    str(uuid4()): [str(uuid4()) for _ in range(N_DEVICES_PER_CUSTOMER)]
    for _ in range(N_CUSTOMERS)
}


def create_mock_data(now=None):
    now = now or timezone.now()
    td = timedelta(seconds=40)

    readings = []

    for i, (cid, dids) in enumerate(MOCK_CUSTOMER_DEVICES.items()):
        customer = Customer.objects.create(id=cid)

        for j, did in enumerate(dids):
            device = Device.objects.create(id=did, customer=customer)

            readings += [
                Reading(
                    device=device,
                    timestamp=now + td * m,
                    reading=i * 100 + j + random()
                )
                for m in range(N_READINGS)
            ]

    Reading.objects.bulk_create(readings)
