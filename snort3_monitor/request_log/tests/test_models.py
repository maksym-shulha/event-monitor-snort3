from django.test import TestCase
from request_log.models import Request
import unittest
from django.core.exceptions import ValidationError
import re


class RequestModelTest(TestCase):

    def setUp(self):
        self.request1 = Request.objects.create(
            user_addr="172.18.0.1",
            http_method="GET",
            timestamp="2023-12-26T10:17:31.480206",
            endpoint="/api/v1/rules/",
            response=200,
            request_data={}
        )

    def test_field_user_addr_lengh(self):
        self.assertIsInstance(self.request1.user_addr, str)
        max_lengh = self.request1._meta.get_field('user_addr').max_length
        self.assertEqual(max_lengh, 50)

    @unittest.expectedFailure
    def test_src_addr_max_length(self):
        long_api_address = "x" * 54
        with self.assertRaises(ValidationError):
            Request.objects.create(
                user_addr=long_api_address,
                http_method="GET",
                timestamp="2023-12-26T10:17:31.480206",
                endpoint="/api/v1/rules/",
                response=200,
                request_data={}
            )

    def test_http_method(self):
        field_label = self.request1._meta.get_field('http_method').verbose_name
        self.assertEqual(field_label, 'http method')
        self.assertIsInstance(self.request1.http_method, str)

    def test_field_user_addr(self):
        ip_address_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        self.assertTrue(ip_address_pattern.match(self.request1.user_addr))

    def test_response_data(self):
        self.assertEqual(self.request1.response, 200)

    def test_field_response(self):
        self.assertIsInstance(self.request1.user_addr, str)
        field_label = self.request1._meta.get_field('endpoint').verbose_name
        self.assertEqual(field_label, 'endpoint')

    def test_create_request(self):
        self.assertEqual(self.request1.user_addr, "172.18.0.1")
        self.assertEqual(self.request1.http_method, "GET")

    def test_response_info(self):
        self.assertEqual(self.request1.request_data, {})
