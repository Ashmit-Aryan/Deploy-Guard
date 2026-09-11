from app.services.docker_service import DockerService
from app.services.nginx_service import NginxService
from app.services.health_service import HealthService


class RollbackService:

    def __init__(self):
        self.docker_service = DockerService()
        self.nginx_service = NginxService()
        self.health_service = HealthService()

    def rollback(
        self,
        previous_environment: str,
        failed_container,
        previous_base_url: str
    ):
        # Switch traffic back to the previous environment
        self.nginx_service.switch_traffic(previous_environment)

        # Verify that the previous environment is healthy
        health_url = (
            f"{previous_base_url.rstrip('/')}/health"
        )

        healthy = self.health_service.check(health_url)

        if not healthy:
            return {
                "status": "rollback_failed",
                "reason": "Previous environment is unhealthy",
                "environment": previous_environment
            }

        # Remove the failed deployment
        self.docker_service.stop_container(
            failed_container
        )

        self.docker_service.remove_container(
            failed_container
        )

        return {
            "status": "rolled_back",
            "environment": previous_environment,
            "container": failed_container.name
        }