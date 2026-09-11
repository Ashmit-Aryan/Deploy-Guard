from unittest.mock import MagicMock

from app.services.deployment_service import DeploymentService
from app.services.deployment_status import DeploymentStatus


def create_mock_deployment_service():
    service = DeploymentService()

    service.docker_service = MagicMock()
    service.health_service = MagicMock()
    service.smoke_test_service = MagicMock()
    service.nginx_service = MagicMock()
    service.rollback_service = MagicMock()
    service.monitoring_service = MagicMock()
    return service


def test_inactive_environment_when_blue_is_active():
    service = create_mock_deployment_service()

    assert service.active_environment == "blue"
    assert service.get_inactive_environment() == "green"


def test_inactive_environment_when_green_is_active():
    service = create_mock_deployment_service()

    service.active_environment = "green"

    assert service.get_inactive_environment() == "blue"


def test_deployment_success_to_green():
    service = create_mock_deployment_service()

    container = MagicMock()
    container.name = "deployguard-v2"

    service.docker_service.create_container.return_value = container # pyright: ignore[reportAttributeAccessIssue]
    service.health_service.check.return_value = True # pyright: ignore[reportAttributeAccessIssue]
    service.smoke_test_service.run.return_value = True # pyright: ignore[reportAttributeAccessIssue]

    result = service.deploy(
        image="nginx:alpine",
        container_name="deployguard-v2",
        base_url="http://localhost:8002"
    )

    assert result["status"] == "monitoring"
    assert result["environment"] == "green"
    assert result["container"] == "deployguard-v2"

    service.docker_service.pull_image.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        "nginx:alpine"
    )

    service.docker_service.create_container.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        image="nginx:alpine",
        name="deployguard-v2",
        host_port=8002
    )

    service.docker_service.start_container.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        container
    )

    service.health_service.check.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        "http://localhost:8002/health"
    )

    service.smoke_test_service.run.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        "http://localhost:8002",
        ["/health", "/version"]
    )

    service.nginx_service.switch_traffic.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        "green"
    )

    assert service.active_environment == "green"
    assert service.status == DeploymentStatus.MONITORING


def test_deployment_success_to_blue():
    service = create_mock_deployment_service()

    # Green is currently serving production
    service.active_environment = "green"

    container = MagicMock()
    container.name = "deployguard-v3"

    service.docker_service.create_container.return_value = container # pyright: ignore[reportAttributeAccessIssue]
    service.health_service.check.return_value = True # pyright: ignore[reportAttributeAccessIssue]
    service.smoke_test_service.run.return_value = True # pyright: ignore[reportAttributeAccessIssue]

    result = service.deploy(
        image="nginx:alpine",
        container_name="deployguard-v3",
        base_url="http://localhost:8001"
    )

    assert result["status"] == "monitoring"
    assert result["environment"] == "blue"
    assert result["container"] == "deployguard-v3"

    service.docker_service.create_container.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        image="nginx:alpine",
        name="deployguard-v3",
        host_port=8001
    )

    service.health_service.check.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        "http://localhost:8001/health"
    )

    service.smoke_test_service.run.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        "http://localhost:8001",
        ["/health", "/version"]
    )

    service.nginx_service.switch_traffic.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        "blue"
    )

    assert service.active_environment == "blue"
    assert service.status == DeploymentStatus.MONITORING


def test_deployment_health_check_failure():
    service = create_mock_deployment_service()

    container = MagicMock()
    container.name = "deployguard-broken"

    service.docker_service.create_container.return_value = container # pyright: ignore[reportAttributeAccessIssue]
    service.health_service.check.return_value = False # pyright: ignore[reportAttributeAccessIssue]

    result = service.deploy(
        image="nginx:alpine",
        container_name="deployguard-broken",
        base_url="http://localhost:8002"
    )

    assert result["status"] == "failed"
    assert result["reason"] == "Health check failed"
    assert result["environment"] == "green"

    assert service.status == DeploymentStatus.FAILED

    service.docker_service.stop_container.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        container
    )

    service.docker_service.remove_container.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        container
    )

    # Smoke test should never run
    service.smoke_test_service.run.assert_not_called() # pyright: ignore[reportAttributeAccessIssue]

    # Traffic must not be switched
    service.nginx_service.switch_traffic.assert_not_called() # pyright: ignore[reportAttributeAccessIssue]

    # Blue remains production
    assert service.active_environment == "blue"


def test_deployment_smoke_test_failure():
    service = create_mock_deployment_service()

    container = MagicMock()
    container.name = "deployguard-broken"

    service.docker_service.create_container.return_value = container # pyright: ignore[reportAttributeAccessIssue]

    # Health check passes
    service.health_service.check.return_value = True # pyright: ignore[reportAttributeAccessIssue]

    # Smoke test fails
    service.smoke_test_service.run.return_value = False # pyright: ignore[reportAttributeAccessIssue]

    result = service.deploy(
        image="nginx:alpine",
        container_name="deployguard-broken",
        base_url="http://localhost:8002"
    )

    assert result["status"] == "failed"
    assert result["reason"] == "Smoke test failed"
    assert result["environment"] == "green"

    assert service.status == DeploymentStatus.FAILED

    service.health_service.check.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        "http://localhost:8002/health"
    )
 
    service.smoke_test_service.run.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        "http://localhost:8002",
        ["/health", "/version"]
    )

    service.docker_service.stop_container.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        container
    )

    service.docker_service.remove_container.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        container
    )

    # Traffic must never reach the broken deployment
    service.nginx_service.switch_traffic.assert_not_called() # pyright: ignore[reportAttributeAccessIssue]

    # Blue remains production
    assert service.active_environment == "blue"

def test_successful_rollback():
    service = create_mock_deployment_service()

    # Green is currently production
    service.active_environment = "green"

    failed_container = MagicMock()
    failed_container.name = "deployguard-v2"

    service.rollback_service.rollback.return_value = { # pyright: ignore[reportAttributeAccessIssue]
        "status": "rolled_back",
        "environment": "blue",
        "container": "deployguard-v2"
    }

    result = service.rollback(
        failed_container=failed_container,
        previous_base_url="http://localhost:8001"
    )

    assert result["status"] == "rolled_back"
    assert result["environment"] == "blue"
    assert result["container"] == "deployguard-v2"

    assert service.status == DeploymentStatus.ROLLED_BACK

    assert service.active_environment == "blue"

    service.rollback_service.rollback.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        previous_environment="blue",
        failed_container=failed_container,
        previous_base_url="http://localhost:8001"
    )

def test_rollback_failure():
    service = create_mock_deployment_service()

    # Green is currently production
    service.active_environment = "green"

    failed_container = MagicMock()
    failed_container.name = "deployguard-v2"

    service.rollback_service.rollback.return_value = { # pyright: ignore[reportAttributeAccessIssue]
        "status": "rollback_failed",
        "reason": "Previous environment is unhealthy",
        "environment": "blue"
    }

    result = service.rollback(
        failed_container=failed_container,
        previous_base_url="http://localhost:8001"
    )

    assert result["status"] == "failed"
    assert result["reason"] == "Previous environment is unhealthy"
    assert result["environment"] == "blue"

    assert service.status == DeploymentStatus.FAILED

    # Green remains the recorded active environment
    assert service.active_environment == "green"

    service.rollback_service.rollback.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        previous_environment="blue",
        failed_container=failed_container,
        previous_base_url="http://localhost:8001"
    )

def test_monitoring_marks_deployment_success_when_healthy():
    service = create_mock_deployment_service()

    service.active_environment = "green"

    failed_container = MagicMock()
    failed_container.name = "deployguard-v2"

    service.monitoring_service.is_healthy.return_value = True # pyright: ignore[reportAttributeAccessIssue]

    result = service.monitor(
        total_requests=100,
        failed_requests=2,
        failed_container=failed_container,
        previous_base_url="http://localhost:8001"
    )

    assert result["status"] == "success"
    assert result["environment"] == "green"

    assert service.status == DeploymentStatus.SUCCESS
    assert service.active_environment == "green"

    service.monitoring_service.is_healthy.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        total_requests=100,
        failed_requests=2
    )

    service.rollback_service.rollback.assert_not_called() # pyright: ignore[reportAttributeAccessIssue]

def test_monitoring_triggers_automatic_rollback():
    service = create_mock_deployment_service()

    # Green is currently serving production
    service.active_environment = "green"

    failed_container = MagicMock()
    failed_container.name = "deployguard-v2"

    # Monitoring detects unhealthy deployment
    service.monitoring_service.is_healthy.return_value = False # pyright: ignore[reportAttributeAccessIssue]

    # Rollback succeeds
    service.rollback_service.rollback.return_value = { # pyright: ignore[reportAttributeAccessIssue]
        "status": "rolled_back",
        "environment": "blue",
        "container": "deployguard-v2"
    }

    result = service.monitor(
        total_requests=100,
        failed_requests=10,
        failed_container=failed_container,
        previous_base_url="http://localhost:8001"
    )

    assert result["status"] == "rolled_back"
    assert result["environment"] == "blue"

    assert service.status == DeploymentStatus.ROLLED_BACK

    # Production should now be Blue
    assert service.active_environment == "blue"

    service.monitoring_service.is_healthy.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        total_requests=100,
        failed_requests=10
    )

    service.rollback_service.rollback.assert_called_once_with( # pyright: ignore[reportAttributeAccessIssue]
        previous_environment="blue",
        failed_container=failed_container,
        previous_base_url="http://localhost:8001"
    )