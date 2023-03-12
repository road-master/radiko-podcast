"""Tests for requester.py."""
import pytest
from radikoplaylist.exceptions import BadHttpStatusCodeError, HttpRequestTimeoutError
from requests import Timeout
import requests_mock as requests_mock_module
from requests_mock import Mocker

from radikopodcast.radikoapi.requester import Requester


class TestRequester:
    """To unify error check and logging process."""

    @staticmethod
    def test_http_request_timeout_error(requests_mock: Mocker) -> None:
        """Get request with error check and logging process."""
        # Reason: This is not requests but mock.
        requests_mock.get(requests_mock_module.ANY, exc=Timeout)  # nosec: B113
        with pytest.raises(HttpRequestTimeoutError):
            Requester.get("https://example.com")

    @staticmethod
    def test_bad_http_status_code_error(requests_mock: Mocker) -> None:
        """Get request with error check and logging process."""
        # Reason: This is not requests but mock.
        requests_mock.get(requests_mock_module.ANY, status_code=400)  # nosec: B113
        with pytest.raises(BadHttpStatusCodeError):
            Requester.get("https://example.com")
