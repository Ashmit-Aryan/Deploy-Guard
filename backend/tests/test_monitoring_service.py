from app.services.monitoring_service import MonitoringService


def test_error_rate_calculation():
    service = MonitoringService()

    result = service.calculate_error_rate(
        total_requests=100,
        failed_requests=5
    )

    assert result == 0.05


def test_error_rate_with_no_requests():
    service = MonitoringService()

    result = service.calculate_error_rate(
        total_requests=0,
        failed_requests=0
    )

    assert result == 0.0


def test_healthy_when_error_rate_is_below_threshold():
    service = MonitoringService(
        error_threshold=0.05
    )

    result = service.is_healthy(
        total_requests=100,
        failed_requests=3
    )

    assert result is True


def test_healthy_when_error_rate_equals_threshold():
    service = MonitoringService(
        error_threshold=0.05
    )

    result = service.is_healthy(
        total_requests=100,
        failed_requests=5
    )

    assert result is True


def test_unhealthy_when_error_rate_exceeds_threshold():
    service = MonitoringService(
        error_threshold=0.05
    )

    result = service.is_healthy(
        total_requests=100,
        failed_requests=6
    )

    assert result is False


def test_custom_error_threshold():
    service = MonitoringService(
        error_threshold=0.10
    )

    result = service.is_healthy(
        total_requests=100,
        failed_requests=8
    )

    assert result is True