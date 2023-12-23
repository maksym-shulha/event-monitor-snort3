import logging
import time
from unittest import skip
from unittest.mock import patch, mock_open

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RuleAPITests(APITestCase):
    fixtures = ['rule.json']

    @classmethod
    def setUpTestData(cls):
        with open('rule/fixtures/valid_rules.txt') as f:
            cls.valid_rules = f.read()
        with open('rule/fixtures/invalid_rules.txt') as f:
            cls.invalid_rules = f.read()
        cls.logger = logging.getLogger('monitor')

    def test_get_rules(self):
        url = reverse('rules-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_get_filtered_rules_by_one_param(self):
        url = reverse('rules-list') + '?sid=57239'
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_filtered_rules_by_three_params(self):
        url = reverse('rules-list') + '?sid=57239&gid=1&rev=1'
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_filtered_rule_does_not_exist(self):
        url = reverse('rules-list') + '?sid=57239&gid=2'
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 0)

    # @skip('Test may influence results of other tests')
    @patch('script_rules.os.system', side_effect=(0, 0, 0))
    def test_post_updating_valid_rules(self, patched_system):
        url = reverse('rules-create')
        with self.assertLogs(self.logger, level='INFO') as log:
            with patch('script_rules.open', mock_open(read_data=self.valid_rules)):
                self.client.post(url)
            time.sleep(0.1)
            self.assertIn('2 new rules have been added.', log.output[0])

    # @skip('Test may influence results of other tests')
    @patch('script_rules.os.system', side_effect=(0, 0, 0))
    def test_post_updating_invalid_rules(self, patched_system):
        url = reverse('rules-create')
        with self.assertLogs(self.logger, level='ERROR') as log:
            with patch('script_rules.open', mock_open(read_data=self.invalid_rules)):
                self.client.post(url)
            time.sleep(0.1)
            self.assertIn("Rule's data is not full:", log.output[0])
