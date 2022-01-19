import random
from math import floor
from urllib.parse import quote_plus
from datetime import timedelta
from uuid import uuid4

from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase

from .mock_data import MOCK_CUSTOMER_DEVICES, create_mock_data

_mock_customer_ids = list(MOCK_CUSTOMER_DEVICES)

_mock_customer_items = list(MOCK_CUSTOMER_DEVICES.items())


def _mock_timestamp():
    return (timezone.now() + timedelta(hours=random.random())).isoformat()


def _mock_reading_input(customer_id=None, device_id=None):
    customer_id = customer_id or random.choice(_mock_customer_ids)
    device_id = device_id or random.choice(MOCK_CUSTOMER_DEVICES[customer_id])

    return {
        'customer_id': customer_id,
        'device_id': device_id,
        'reading': random.random() * 10,
        'timestamp': _mock_timestamp(),
    }


class AddReadingsViewTests(APITestCase):

    def test_can_insert_multiple_readings(self):
        data = [
            _mock_reading_input()
            for _ in range(10)
        ]

        url = reverse('api-readings')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.json()), len(data))

    def test_can_insert_multiple_readings_of_same_device(self):
        device_id = str(uuid4())
        customer_id = str(uuid4())

        data = [
            _mock_reading_input(customer_id, device_id)
            for _ in range(10)
        ]

        url = reverse('api-readings')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.json()), len(data))

    def test_devices_cannot_be_shared_accross_customers(self):
        device_id = str(uuid4())
        customer_id_a = str(uuid4())
        customer_id_b = str(uuid4())

        data = [
            _mock_reading_input(customer_id_a, device_id),
            _mock_reading_input(customer_id_b, device_id),
        ]
        url = reverse('api-readings')

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)


class ListReadingsByTests(APITestCase):

    def setUp(self):
        self.now = timezone.now()
        create_mock_data(self.now)

    def test_can_list_readings_by_device(self):
        customer_id, device_ids = _mock_customer_items[2]
        device_id = device_ids[1]

        url = reverse('api-device-readings', kwargs=dict(device_id=device_id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        data = response.json()['data']

        self.assertEqual(1, len(data))

        for d in data:
            self.assertEqual(customer_id, d['customer_id'])
            self.assertIsNone(d['from_date'])
            self.assertIsNone(d['to_date'])
            self.assertEqual(5, d['aggregation_size_minutes'])
            self.assertTrue(d['aggregated_values'])
            self.assertIn('value', d['aggregated_values'][0])
            self.assertIn('from', d['aggregated_values'][0])

            for av in d['aggregated_values']:
                self.assertEqual(
                    2 * 100 + MOCK_CUSTOMER_DEVICES[customer_id].index(d['device_id']),
                    floor(av['value']),
                )

            t_0 = parse_datetime(d['aggregated_values'][0]['from'])
            t_1 = parse_datetime(d['aggregated_values'][1]['from'])

            self.assertEqual(timedelta(minutes=5), t_1 - t_0)

    def test_can_list_readings_by_customer(self):
        customer_id, device_ids = _mock_customer_items[2]

        url = reverse('api-customer-readings', kwargs=dict(customer_id=customer_id))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        data = response.json()['data']

        self.assertEqual(len(device_ids), len(data))

        for d in data:
            self.assertEqual(customer_id, d['customer_id'])
            self.assertIsNone(d['from_date'])
            self.assertIsNone(d['to_date'])
            self.assertEqual(5, d['aggregation_size_minutes'])
            self.assertTrue(d['aggregated_values'])
            self.assertIn('value', d['aggregated_values'][0])
            self.assertIn('from', d['aggregated_values'][0])

            for av in d['aggregated_values']:
                self.assertEqual(
                    2 * 100 + MOCK_CUSTOMER_DEVICES[customer_id].index(d['device_id']),
                    floor(av['value']),
                )

            t_0 = parse_datetime(d['aggregated_values'][0]['from'])
            t_1 = parse_datetime(d['aggregated_values'][1]['from'])

            self.assertEqual(timedelta(minutes=5), t_1 - t_0)

    def test_from_date_filter(self):
        device_id = _mock_customer_items[0][1][0]
        from_date = self.now + timedelta(seconds=400)

        url = reverse('api-device-readings', kwargs=dict(device_id=device_id))
        url += f'?from_date={quote_plus(from_date.isoformat())}'

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        data = response.json()['data'][0]

        self.assertEqual(from_date, parse_datetime(data['from_date']))
        self.assertIsNone(data['to_date'])
        self.assertTrue(data['aggregated_values'])

    def test_to_date_filter(self):
        device_id = _mock_customer_items[0][1][0]
        to_date = self.now + timedelta(seconds=400)

        url = reverse('api-device-readings', kwargs=dict(device_id=device_id))
        url += f'?to_date={quote_plus(to_date.isoformat())}'

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        data = response.json()['data'][0]

        self.assertIsNone(data['from_date'])
        self.assertEqual(to_date, parse_datetime(data['to_date']))
        self.assertTrue(data['aggregated_values'])

    def test_aggregation_size(self):
        device_id = _mock_customer_items[0][1][0]
        size = 10

        url = reverse('api-device-readings', kwargs=dict(device_id=device_id))
        url += f'?aggregation_size_minutes={size}'

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        data = response.json()['data'][0]

        self.assertEqual(data['aggregation_size_minutes'], size)
        self.assertTrue(data['aggregated_values'])

        t_0 = parse_datetime(data['aggregated_values'][0]['from'])
        t_1 = parse_datetime(data['aggregated_values'][1]['from'])

        self.assertEqual(timedelta(minutes=10), t_1 - t_0)
