from django.test import TestCase
from rest_framework.test import APIClient


class TestRateEndpoint(TestCase):
    def test_rate_post_request__succeed(self):
        car = {"make": "honda", "model": "CBX"}
        asserted_code = 201
        endpoint = "/cars/"
        c = APIClient()
        response = c.post(endpoint, data=car)
        self.assertEqual(asserted_code, response.status_code)
        car_id = response.data["id"]

        c = APIClient()
        endpoint = "/rate/"
        data = {"car_id": car_id, "rate": 1}
        asserted_response_data = {"car_id": car_id, "rate": 1}
        response = c.post(endpoint, data=data)
        self.assertEqual(asserted_code, response.status_code)
        self.assertEqual(asserted_response_data, response.json())

    def test_rate_post_request_with_not_existing_id__fail(self):

        expected_code = 404
        car_id = 999

        c = APIClient()
        endpoint = "/rate/"
        data = {"car_id": car_id, "rate": 1}
        expected_content = {"car_id": ["Car ID 999 does not exist."]}
        response = c.post(endpoint, data=data)
        self.assertEqual(expected_code, response.status_code)
        self.assertEqual(expected_content, response.data)

    def test_rate_post_request_without_trailing_slash__succeed(self):

        expected_code = 403
        expected_content = {
            "car_id": ["This field is required."],
            "rate": ["This field is required."],
        }
        data = {}

        c = APIClient()
        endpoint = "/rate"
        response = c.post(endpoint, data=data)
        self.assertEqual(expected_code, response.status_code)
        self.assertEqual(expected_content, response.data)
