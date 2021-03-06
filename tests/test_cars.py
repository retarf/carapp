from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from cars.requests import ModelListRequest, ModelListRequestError


class TestModelListRequestMethods(TestCase):
    def test_url(self):
        car_make = "honda"
        models = ModelListRequest(f"{car_make}")
        asserted_url = (
            f"https://vpic.nhtsa.dot.gov/api"
            f"/vehicles/GetModelsForMake/{car_make}?format=json"
        )
        self.assertEqual(asserted_url, models.url)

    def test_get_car_model_list(self):
        """This test check 10-th element of the list"""
        car_make = "honda"
        asserted_list_element = {
            "Make_ID": 474,
            "Make_Name": "HONDA",
            "Model_ID": 2128,
            "Model_Name": "CR-Z",
        }
        list_element = ModelListRequest(f"{car_make}").get_car_make_model_list()[10]
        self.assertEqual(asserted_list_element, list_element)

    def test_get_car_make_model__succeed(self):
        car_make = "honda"
        model_name = "CBX"
        asserted_model_dict = {
            "Make_ID": 474,
            "Make_Name": "HONDA",
            "Model_ID": 27546,
            "Model_Name": "CBX",
        }
        model_list = ModelListRequest(f"{car_make}")
        model_dict = model_list.get_car_make_model(model_name)
        self.assertEqual(asserted_model_dict, model_dict)

    def test_get_car_make_mode__raise_exception(self):
        car_make = "honda"
        model_name = "AAA"
        model_list = ModelListRequest(f"{car_make}")
        self.assertRaises(
            ModelListRequestError, model_list.get_car_make_model, model_name
        )


class TestCarsEndpoint(TestCase):
    def test_cars_post_request__succeed(self):
        request_data = {"make": "honda", "model": "CBX"}
        asserted_response_data = {
            "Make_ID": 474,
            "Make_Name": "HONDA",
            "Model_ID": 27546,
            "Model_Name": "CBX",
        }
        asserted_code = 201
        endpoint = "/cars/"
        c = APIClient()
        response = c.post(endpoint, data=request_data)
        asserted_response_data["id"] = response.data["id"]
        self.assertEqual(asserted_code, response.status_code)
        self.assertEqual(asserted_response_data, response.data)

    def test_cars_post_request__fail__wrong_model(self):
        request_data = {"make": "honda", "model": "CB"}
        asserted_code = 404
        endpoint = "/cars/"
        c = APIClient()
        response = c.post(endpoint, data=request_data)
        self.assertEqual(asserted_code, response.status_code)

    def test_cars_post_request__fail__wrong_make(self):
        request_data = {"make": "honey", "model": "CBX"}
        asserted_code = 404
        endpoint = "/cars/"
        c = APIClient()
        response = c.post(endpoint, data=request_data)
        self.assertEqual(asserted_code, response.status_code)

    def test_cars_post_request__fail__already_exists(self):
        request_data = {"make": "honda", "model": "CBX"}
        asserted_code = 403
        endpoint = "/cars/"
        c = APIClient()
        c.post(endpoint, data=request_data)
        response = c.post(endpoint, data=request_data)
        self.assertEqual(asserted_code, response.status_code)

    def test_cars_post_request__fail__wrong_payload(self):
        request_data = {"make": "Volkswagen"}
        asserted_code = 403
        endpoint = "/cars/"
        c = APIClient()
        c.post(endpoint, data=request_data)
        response = c.post(endpoint, data=request_data)
        expected_response_data = {"model": ["This field is required."]}
        self.assertEqual(asserted_code, response.status_code)
        self.assertEqual(expected_response_data, response.data)

    def test_cars_get_request__succeed(self):
        request_data = {"make": "honda", "model": "CBX"}
        endpoint = "/cars/"
        c = APIClient()
        response = c.post(endpoint, data=request_data)
        asserted_code = 201
        self.assertEqual(asserted_code, response.status_code)
        car_id = response.data["id"]

        endpoint = "/rate/"
        rates = [3, 5, 1]
        for r in rates:
            request_data = {"car_id": car_id, "rate": r}
            response = c.post(endpoint, data=request_data)
            self.assertEqual(asserted_code, response.status_code)

        endpoint = "/cars/"
        response = c.get(endpoint)
        asserted_average = 3.0
        asserted_code = 200
        asserted_response_data = [
            {
                "id": car_id,
                "make": "HONDA",
                "make_id": 474,
                "model": "CBX",
                "model_id": 27546,
                "average_rate": asserted_average,
            }
        ]
        self.assertEqual(asserted_code, response.status_code)
        self.assertEqual(asserted_response_data, response.json())

    def test_cars_post_request_without_trailing_slash__succeed(self):

        expected_code = 403
        expected_content = {
            "make": ["This field is required."],
            "model": ["This field is required."],
        }
        data = {}

        c = APIClient()
        endpoint = "/cars"
        response = c.post(endpoint, data=data)
        self.assertEqual(expected_code, response.status_code)
        self.assertEqual(expected_content, response.data)

    @patch("cars.requests.urllib.request.urlopen")
    def test_cars_post_request_with_api_error__fail(self, urlopen):
        expected_content = "test error"
        urlopen.side_effect = Exception(expected_content)
        expected_code = 502
        data = {"make": "Volkswagen", "model": "Golf"}

        c = APIClient()
        endpoint = "/cars"
        response = c.post(endpoint, data=data)
        self.assertEqual(expected_code, response.status_code)
        self.assertEqual(expected_content, response.data)
