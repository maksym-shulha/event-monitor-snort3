import logging
from unittest.mock import patch

from django.http import HttpRequest
from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from rule.models import Rule
from rule.views import RuleListView, RuleCreate


class RuleCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.logger = logging.getLogger('monitor')
        cls.view = RuleCreate()
        cls.request = HttpRequest()

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
        with self.assertLogs(self.logger, level='INFO') as log:
            self.view.background_update()
            patched_update_pulled_pork.assert_called()
            self.assertIn('1 new rules have been added.', log.output[0])

    @patch('rule.views.update_pulled_pork', side_effect=RuntimeError('Test error'))
    def test_unsuccessful_updating(self, patched_update_pulled_pork):
        with self.assertLogs(self.logger, level='ERROR') as log:
            self.view.background_update()
            patched_update_pulled_pork.assert_called()
            self.assertIn('Test error', log.output[0])


class RuleListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.view = RuleListView()
        cls.factory = RequestFactory()
        cls.view.request = cls.factory.get('/')
        Rule.objects.create(sid=123, rev=456, gid=789)
        Rule.objects.create(sid=124, rev=457, gid=790)
        Rule.objects.create(sid=125, rev=458, gid=791)

    def test_valid_query_params(self):
        entered = ['param1', 'param2']
        allowed = ['param1', 'param2']
        self.assertIsNone(self.view.validate_params(entered, allowed))

    def test_invalid_query_params(self):
        entered = ['param1', 'param2', 'param3']
        allowed = ['param1', 'param2']
        with self.assertRaises(ValidationError) as e:
            self.view.validate_params(entered, allowed)
        self.assertEqual(
            str(e.exception),
            "{'error': ErrorDetail(string='You can use only param1, param2, page as query filters.', code='invalid')}"
        )

    def test_page_is_allowed_in_query_param(self):
        entered = ['param1', 'param2', 'page']
        allowed = ['param1', 'param2']
        self.assertIsNone(self.view.validate_params(entered, allowed))

    @patch('rule.views.RuleListView.validate_params')
    def test_filtering_by_sid(self, patched_validate_params):
        self.view.request.query_params = {'sid': '123'}
        queryset = self.view.get_queryset()
        self.assertIn(123, [item.sid for item in queryset])

    @patch('rule.views.RuleListView.validate_params')
    def test_filtering_by_rev(self, patched_validate_params):
        self.view.request.query_params = {'rev': '456'}
        queryset = self.view.get_queryset()
        self.assertIn(456, [item.rev for item in queryset])

    @patch('rule.views.RuleListView.validate_params')
    def test_filtering_by_gid(self, patched_validate_params):
        self.view.request.query_params = {'gid': '789'}
        queryset = self.view.get_queryset()
        self.assertIn(789, [item.gid for item in queryset])

    @patch('rule.views.RuleListView.validate_params')
    def test_few_query_params(self, patched_validate_params):
        self.view.request.query_params = {'sid': '123', 'rev': '456', 'gid': '789'}
        queryset = self.view.get_queryset()
        self.assertIn((123, 456, 789), [(item.sid, item.rev, item.gid) for item in queryset])

    @patch('rule.views.RuleListView.validate_params')
    def test_ordering_of_queryset(self, patched_validate_params):
        self.view.request.query_params = {}
        queryset = self.view.get_queryset()
        self.assertLessEqual(queryset.first().sid, queryset.last().sid)
