from datetime import datetime

from django.test import TestCase
from django.db.utils import IntegrityError, DataError
from django.http.response import Http404
from django.db.models.deletion import ProtectedError

from monitor.models import Rule, Event


class RuleModelCreationTests(TestCase):
    def test_with_required_fields(self):
        instance = Rule.objects.create(sid=1, rev=1, gid=2, action="alert")
        self.assertTupleEqual((instance.sid, instance.gid, instance.rev), (1, 2, 1))

    def test_without_required_fields(self):
        with self.assertRaises(IntegrityError):
            Rule.objects.create(sid=1, rev=1, action="alert")

    def test_invalid_alert(self):
        with self.assertRaises(DataError):
            Rule.objects.create(sid=1, rev=1, gid=2, action="a"*51)


class RuleModelGeneralTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        rule1 = {
            "gid": 1,
            "sid": 53159,
            "rev": 1,
            "action": "alert",
            "message": "MALWARE-OTHER Win.Trojan.ObliqueRAT download attempt"
                }
        rule2 = {
            "gid": 1,
            "sid": 53158,
            "rev": 1,
            "action": "alert",
            "message": "MALWARE-OTHER Win.Trojan.ObliqueRAT download attempt"
                }
        cls.rule = Rule.objects.create(**rule1)
        cls.rule_with_event = Rule.objects.create(**rule2)
        cls.event = Event.objects.create(rule=cls.rule_with_event, timestamp=datetime.now())

    def test_rule_exists(self):
        instance = Rule.get_rule(gid=1, sid=53159, rev=1)
        self.assertEqual(self.rule, instance)

    def test_rule_does_not_exist(self):
        with self.assertRaises(Http404):
            Rule.get_rule(gid=2, sid=53159, rev=1)

    def test_delete_rule(self):
        self.rule.delete()
        with self.assertRaises(Http404):
            Rule.get_rule(gid=1, sid=53159, rev=1)

    def test_unsuccessful_delete_rule(self):
        with self.assertRaises(ProtectedError):
            self.rule_with_event.delete()
