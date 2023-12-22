from monitor.models import Event
from rule.models import Rule
import datetime
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from collections import OrderedDict


class EventAPIListViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rule = Rule.objects.create(
            sid=1,
            gid=1,
            rev=1,
            action="Test Action",
            message="Test Message",
            data_json={"key": "value"}
        )

        timestamp = datetime.datetime(2023, 1, 1, 12, 0, 0)
        cls.event_1 = Event.objects.create(
            rule=cls.rule,
            timestamp=timestamp,
            src_addr="192.168.1.1",
            proto="TCP",
            src_port=1234,
            dst_addr="10.0.0.1",
            dst_port=80,
        )

        cls.event_2 = Event.objects.create(
            rule=cls.rule,
            timestamp=timestamp,
            src_addr="192.168.1.2",
            proto="UDP",
            src_port=8080,
            dst_addr="10.0.0.2",
            dst_port=80,
        )

    def test_filter_src_addr(self):
        url = reverse('event-list-update')
        response = self.client.get(url, {'src_addr': '192.168.1.1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, OrderedDict)
        self.assertTrue(response.data)

        results = response.data.get('results', [])
        self.assertTrue(results)
        item = results[0] if results else None
        self.assertIn('192.168.1.1', item.get('src_addr', []))
        self.assertEqual(len(results), 1)

    def test_filter_proto(self):
        url = reverse('event-list-update')
        response = self.client.get(url, {'proto': 'UDP'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, OrderedDict)
        self.assertTrue(response.data)

        results = response.data.get('results', [])
        self.assertTrue(results)
        item = results[0] if results else None
        self.assertIn('UDP', item.get('proto', []))
        self.assertEqual(len(results), 1)

    def test_filter_multiple_params(self):
        url = reverse('event-list-update')
        response = self.client.get(url, {'src_addr': '192.168.1.1', 'proto': 'TCP'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, OrderedDict)
        self.assertIsNotNone(response.data)

        results = response.data.get('results', [])
        self.assertTrue(results)

        item = results[0] if results else None
        self.assertEqual(item.get('src_addr'), '192.168.1.1')
        self.assertEqual(item.get('proto'), 'TCP')
        self.assertEqual(len(results), 1)

    def test_filetr_multiple_different_params(self):
        url = reverse('event-list-update')
        response = self.client.get(url, {'dst_port': '80', 'dst_port': '80'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get('results', [])
        self.assertTrue(results)
        self.assertEqual(len(results), 2)
        item1 = results[0] if results else None
        item2 = results[1] if len(results) > 1 else None

        self.assertEqual(item1.get('dst_port'), 80)
        self.assertEqual(item2.get('dst_port'), 80)

    def test_invalid_params(self):
        url = reverse('event-list-update')
        response = self.client.get(url, {'addee': 'fo'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_method_no_filtering(self):
        url = reverse('event-list-update')
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "All events are marked as deleted."})

        events = Event.objects.all()
        self.assertEqual(events.count(), 2)
        for event in events:
            self.assertTrue(event.mark_as_deleted)

    def test_order_by_id(self):
        url = reverse('event-list-update')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', [])

        self.assertEqual([result['id'] for result in results], sorted([1, 2]))
