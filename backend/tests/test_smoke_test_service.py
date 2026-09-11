from unittest.mock import patch, MagicMock

from app.services.smoke_test_service import SmokeTestService


def test_check_endpoint_success():
    service = SmokeTestService()

    with patch("requests.get") as mock_get:
        response = MagicMock()
        response.status_code = 200

        mock_get.return_value = response

        result = service.check_endpoint(
            "http://localhost:8002/health"
        )

        assert result is True


def test_check_endpoint_failure():
    service = SmokeTestService()

    with patch("requests.get") as mock_get:
        response = MagicMock()
        response.status_code = 500

        mock_get.return_value = response

        result = service.check_endpoint(
            "http://localhost:8002/health"
        )

        assert result is False


def test_run_all_endpoints_success():
    service = SmokeTestService()

    with patch.object(
        service,
        "check_endpoint",
        return_value=True
    ) as mock_check:

        result = service.run(
            "http://localhost:8002",
            ["/health", "/version", "/"]
        )

        assert result is True
        assert mock_check.call_count == 3


def test_run_fails_when_endpoint_fails():
    service = SmokeTestService()

    with patch.object(
        service,
        "check_endpoint",
        side_effect=[True, False]
    ) as mock_check:

        result = service.run(
            "http://localhost:8002",
            ["/health", "/version"]
        )

        assert result is False
        assert mock_check.call_count == 2