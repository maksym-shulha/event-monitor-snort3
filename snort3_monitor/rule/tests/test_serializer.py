from django.test import TestCase

from rule.serializers import RuleSerializer


class RuleSerializerTest(TestCase):
    def test_valid_data(self):
        data = {
            'sid': 1,
            'rev': 2,
            'gid': 3,
            'action': 'allow',
            'message': 'Test Rule'
        }
        serializer = RuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_required(self):
        invalid_data = {
            'sid': 1,
            'rev': 2,
            'action': 'allow',
            'message': 'Test Rule'
        }
        serializer = RuleSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), {'gid'})

    def test_invalid_data_type(self):
        invalid_data = {
            'sid': 1,
            'rev': 2,
            'gid': 'not number',
            'action': 'allow',
            'message': 'Test Rule'
        }
        serializer = RuleSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), {'gid'})
