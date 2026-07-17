"""Tests for wattnet.client._util."""

import requests

from wattnet.client._util import error_detail


def test_error_detail_extracts_json_detail_field():
    response = requests.Response()
    response.status_code = 400
    response._content = b'{"detail": "Invalid input parameters"}'

    assert error_detail(response) == "Invalid input parameters"


def test_error_detail_falls_back_to_text_on_non_json_body():
    response = requests.Response()
    response.status_code = 500
    response._content = b"Internal Server Error"

    assert error_detail(response) == "Internal Server Error"
