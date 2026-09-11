from unittest.mock import MagicMock

from app.services.rollback_service import RollbackService


def create_mock_rollback_service():
    service = RollbackService()

    service.docker_service = MagicMock()
    service.nginx_service = MagicMock()
    service.health_service = MagicMock()

    return service


def test_successful_rollback():
    service = create_mock_rollback_service()

    failed_container = MagicMock()
    failed_container.name = "deployguard-v2"

    service.health_service.check.return_value = True

    result = service.rollback(
        previous_environment="blue",
        failed_container=failed_container,
        previous_base_url="http://localhost:8001"
    )

    assert result["status"] == "rolled_back"
    assert result["environment"] == "blue"
    assert result["container"] == "deployguard-v2"

    # Traffic must be switched back
    service.nginx_service.switch_traffic.assert_called_once_with(
        "blue"
    )

    # Previous environment must be verified
    service.health_service.check.assert_called_once_with(
        "http://localhost:8001/health"
    )

    # Failed container must be cleaned up
    service.docker_service.stop_container.assert_called_once_with(
        failed_container
    )

    service.docker_service.remove_container.assert_called_once_with(
        failed_container
    )


def test_rollback_fails_if_previous_environment_is_unhealthy():
    service = create_mock_rollback_service()

    failed_container = MagicMock()
    failed_container.name = "deployguard-v2"

    service.health_service.check.return_value = False

    result = service.rollback(
        previous_environment="blue",
        failed_container=failed_container,
        previous_base_url="http://localhost:8001"
    )

    assert result["status"] == "rollback_failed"
    assert result["reason"] == "Previous environment is unhealthy"
    assert result["environment"] == "blue"

    # Traffic should still be switched back first
    service.nginx_service.switch_traffic.assert_called_once_with(
        "blue"
    )

    service.health_service.check.assert_called_once_with(
        "http://localhost:8001/health"
    )

    # Do NOT destroy the failed container because
    # rollback has not been verified successfully
    service.docker_service.stop_container.assert_not_called()

    service.docker_service.remove_container.assert_not_called()