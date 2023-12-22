from django.test import TestCase
from django.core.exceptions import ValidationError
from  monitor.views import validate_params
import unittest
from unittest import mock
from monitor.views import EventListUpdate


class EventListUpdateViewTest(TestCase):
    
    def test_valid_params(self):
        allowed_params = ['src_addr', 'src_port', 'dst_addr', 'dst_port', 'sid', 'proto']
        entered_params = ['src_addr', 'dst_port']
        
        try:
            validate_params(entered_params, allowed_params)
        except ValidationError:
            self.fail("validate_params raised ValidationError unexpectedly.")
    
    @unittest.expectedFailure
    def test_invalid_params(self):
        allowed_params = ['src_addr', 'src_port', 'dst_addr', 'dst_port', 'sid', 'proto']
        entered_params = ['src_addr', 'invalid_param']
        
        with self.assertRaises(ValidationError) as context:
            validate_params(entered_params, allowed_params)
        
        self.assertEqual(
            context.exception.message,
            {
                "error": "Invalid query parameters: invalid_param. "
                        "Allowed parameters are: src_addr, src_port, dst_addr, dst_port, sid, proto, page."
            }
        )
        
    def test_valid_params_empty(self):
        allowed_params = ['src_addr', 'src_port', 'dst_addr', 'dst_port', 'sid', 'proto']
        entered_params = []
        
        result =  validate_params(entered_params, allowed_params)
        self.assertIsNone(result)
    
    def test_get_queryset_error(self):
        with mock.patch('monitor.views.Event.objects.filter', side_effect=Exception()):
            with self.assertRaises(Exception):
                EventListUpdate.get_queryset({})
 
                


    