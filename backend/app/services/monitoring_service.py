class MonitoringService:

    def __init__(self, error_threshold: float = 0.05):
        self.error_threshold = error_threshold

    def calculate_error_rate(
        self,
        total_requests: int,
        failed_requests: int
    ) -> float:

        if total_requests <= 0:
            return 0.0

        return failed_requests / total_requests

    def is_healthy(
        self,
        total_requests: int,
        failed_requests: int
    ) -> bool:

        error_rate = self.calculate_error_rate(
            total_requests,
            failed_requests
        )

        return error_rate <= self.error_threshold