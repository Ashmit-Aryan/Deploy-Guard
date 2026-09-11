from app.services.deployment_status import DeploymentStatus
from app.services.deployment_service import DeploymentService


def test_deployment_status_values():
    assert DeploymentStatus.PENDING == "pending"
    assert DeploymentStatus.DEPLOYING == "deploying"
    assert DeploymentStatus.HEALTH_CHECK == "health_check"
    assert DeploymentStatus.SMOKE_TEST == "smoke_test"
    assert DeploymentStatus.SWITCHING == "switching"
    assert DeploymentStatus.MONITORING == "monitoring"
    assert DeploymentStatus.SUCCESS == "success"
    assert DeploymentStatus.FAILED == "failed"
    assert DeploymentStatus.ROLLING_BACK == "rolling_back"
    assert DeploymentStatus.ROLLED_BACK == "rolled_back"


def test_deployment_service_starts_pending():
    service = DeploymentService()

    assert service.status == DeploymentStatus.PENDING

def test_deployment_service_can_change_status():
    service = DeploymentService()

    service.set_status(DeploymentStatus.DEPLOYING)

    assert service.status == DeploymentStatus.DEPLOYING