import logging
from unittest.mock import patch

from django.http import HttpRequest
from django.test import TestCase
from rest_framework import status
from rest_framework.response import Response

from rule.views import RuleListView, RuleCreate


logger = logging.getLogger('monitor')


class RuleCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.view = RuleCreate()
        cls.request = HttpRequest()
        cls.request.method = 'POST'
        cls.request.data = {'key': 'value'}

    @patch('rule.views.RuleCreate.background_update')
    def test_post_runs_updating(self, patched_background_update):
        self.view.post(self.request)
        patched_background_update.assert_called()

    @patch('rule.views.RuleCreate.background_update')
    def test_post_returns_response(self, patched_background_update):
        response = self.view.post(self.request)
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data, {'message': 'Update process started.'})

    @patch('rule.views.update_pulled_pork', return_value=1)
    def test_successful_updating(self, patched_update_pulled_pork):
        with self.assertLogs(logger, level='INFO') as log:
            self.view.background_update()
            patched_update_pulled_pork.assert_called()
            self.assertIn('1 new rules have been added.', log.output[0])

    @patch('rule.views.update_pulled_pork', side_effect=RuntimeError('Test error'))
    def test_unsuccessful_updating(self, patched_update_pulled_pork):
        with self.assertLogs(logger, level='ERROR') as log:
            self.view.background_update()
            patched_update_pulled_pork.assert_called()
            self.assertIn('Test error', log.output[0])

