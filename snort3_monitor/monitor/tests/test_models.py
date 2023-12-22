from django.test import TestCase
import unittest
from monitor.models import Event
from rule.models import Rule
import datetime
from django.core.exceptions import ValidationError

class EventModelTest(TestCase):

    def setUp(self):
        self.rule = Rule.objects.create(
            sid=1,
            gid=1,
            rev=1,
            action="Test Action",
            message="Test Message",
            data_json={})

        self.event = Event.objects.create(
            rule=self.rule,
            timestamp=datetime.datetime.now(),
            src_addr="192.168.1.1",
            proto="TCP")

    def test_rule_relationship(self):
        self.assertEqual(self.event.rule, self.rule)

    def test_proto_type(self):
        self.assertIsInstance(self.event.proto, str)

    def test_cascade_deletion(self):
        self.event.delete()
        self.assertFalse(Event.objects.filter(pk=self.rule.pk).exists())

    def test_max_lengh_src_addr(self):
        max_lengh = self.event._meta.get_field('src_addr').max_length
        self.assertEqual(max_lengh, 128)

    @unittest.expectedFailure
    def test_max_lengh_src_addr(self):
        max_lengh = self.event._meta.get_field('src_addr').max_length
        self.assertEqual(max_lengh, 125)

    def test_dst_port_null_blank(self):
        self.event.dst_port = None
        self.event.save()
        self.assertIsNone(self.event.dst_port)

    @unittest.expectedFailure
    def test_src_addr_max_length(self):
        long_address = "x" * 129
        with self.assertRaises(ValidationError):
            Event.objects.create(rule=self.rule,
                                 timestamp=datetime.datetime.now(),
                                 src_addr=long_address)

    def test_proto(self):
        self.assertIsNotNone(self.event.proto)

    def test_timestamp_field(self):
        field_label = self.event._meta.get_field('timestamp').verbose_name
        self.assertEqual(field_label, 'timestamp')

    def test_src_addr_max_length(self):
        event = Event(src_addr="1234567890123456789012345678901234567890")
        self.assertRaises(ValidationError, event.full_clean)

    def test_action(self):
        self.assertNotIsInstance(self.event.timestamp, int)
