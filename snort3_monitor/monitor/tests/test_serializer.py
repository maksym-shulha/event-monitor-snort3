from django.test import TestCase
import unittest
from monitor.models import Event
from rule.models import Rule
import datetime
from monitor.serializers import EventSerializer, EventCountAddressSerializer, EventCountRuleSerializer


class EventSerializerTest(TestCase):

    def setUp(self):
        self.rule = Rule.objects.create(
            sid=1,
            gid=1,
            rev=1,
            action="Test Action",
            message="Test Message",
            data_json={"key": "value"}
        )

        self.event = Event.objects.create(
            rule=self.rule,
            timestamp=datetime.datetime.now(),
            src_addr="192.168.1.1",
            proto="TCP",
            src_port=1234,
            dst_addr="10.0.0.1",
            dst_port=80,
        )

    def test_data_serialization(self):
        serializer = EventSerializer(self.event)
        serialized_data = serializer.data

        self.assertEqual(serialized_data["id"], self.event.pk)
        self.assertEqual(serialized_data["timestamp"], self.event.timestamp.isoformat())
        self.assertEqual(serialized_data["src_addr"], self.event.src_addr)
        self.assertEqual(serialized_data["proto"], self.event.proto)

    @unittest.expectedFailure
    def test_invalid_data_validation(self):
        invalid_data = {
            'rule': 123,
            'timestamp': "invalid_format",
            'src_addr': "",
        }

        serializer = EventSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 4)
        self.assertIn('rule', serializer.errors)
        self.assertIn('timestamp', serializer.errors)
        self.assertIn('src_addr', serializer.errors)

    def test_dst_port(self):
        self.assertIsInstance(self.event.dst_port, int)

    def test_invalid_dst_port_validation(self):
        invalid_data = {
            'dst_port': "invalid_port",
        }
        serializer = EventSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('dst_port', serializer.errors)

    def test_required_fields_existence(self):
        serializer = EventSerializer(data={
            'rule': self.rule.pk,
            'timestamp': self.event.timestamp.isoformat(),
            'src_addr': self.event.src_addr,
            'dst_addr': self.event.dst_addr,
            'proto': self.event.proto,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_get_sid(self):
        serializer = EventSerializer(instance=self.event)
        self.assertEqual(serializer.get_sid(self.event), self.rule.sid)

    def test_get_action(self):
        serializer = EventSerializer(instance=self.event)
        self.assertEqual(serializer.get_action(self.event), self.rule.action)

    def test_get_message(self):
        serializer = EventSerializer(instance=self.event)
        self.assertEqual(serializer.get_message(self.event), self.rule.message)


class EventCountAddrTest(TestCase):

    def test_valid_data(self):
        valid_data = {'addr_pair': '192.168.1.1', 'count': 1}
        serializer = EventCountAddressSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_missing_addr_pair(self):
        invalid_data = {'count': 1}
        serializer = EventCountAddressSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('addr_pair', serializer.errors)

    def test_invalid_count(self):
        invalid_data = {'addr_pair': '192.168.1.1', 'count': 'invalid_count'}
        serializer = EventCountAddressSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('count', serializer.errors)

    def test_max_length_addr_pair(self):
        valid_data = {'addr_pair': 'a' * 128, 'count': 10}
        serializer = EventCountAddressSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_exceed_max_length_addr_pair(self):
        valid_data = {'addr_pair': 'a' * 129, 'count': 10}
        serializer = EventCountAddressSerializer(data=valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('addr_pair', serializer.errors)


class EventCountRuleTest(TestCase):

    def test_sid_valid_data(self):
        valid_data = {'sid': 1, 'count': 2}
        serializer = EventCountRuleSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_missing_sid(self):
        invalid_data = {'count': 2}
        serializer = EventCountRuleSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('sid', serializer.errors)

    def test_invalid_data_count(self):
        invalid_count = {'sid': 1, 'count': 'invalid_data'}
        serializer = EventCountRuleSerializer(data=invalid_count)
        self.assertFalse(serializer.is_valid())
        self.assertIn('count', serializer.errors)

    def test_sid_by_int(self):
        valid_data = {'sid': 1, 'count': 1}
        serializer = EventCountRuleSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(int(serializer.validated_data['sid']), 1)
