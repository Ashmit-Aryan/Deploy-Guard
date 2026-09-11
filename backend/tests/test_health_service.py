from app.services.health_service import HealthService


def test_health_check_success():
    health_service = HealthService()

    result = health_service.check("https://httpbin.org/status/200")

    assert result is True


def test_health_check_failure():
    health_service = HealthService()

    result = health_service.check("http://localhost:9999/health")

    assert result is False
