from app.services.docker_service import DockerService
from app.services.health_service import HealthService
from app.services.nginx_service import NginxService
from app.services.smoke_test_service import SmokeTestService
from app.services.rollback_service import RollbackService
from app.services.monitoring_service import MonitoringService
from app.services.deployment_status import DeploymentStatus
from app.models.application import Application
from app.models import deployment
from app.schemas import application
from app.core.config import ENVIRONMENT_PORTS
from sqlalchemy.orm import Session
from app.models.deployment import Deployment
from datetime import datetime
from app.models.instance import Instance


class DeploymentService:

    def __init__(self):
        self.docker_service = DockerService()
        self.nginx_service = NginxService()
        self.health_service = HealthService()
        self.smoke_test_service = SmokeTestService()
        self.rollback_service = RollbackService()
        self.monitoring_service = MonitoringService()

        self.active_environment = "blue"
        self.status = DeploymentStatus.PENDING

    def set_status(self, status: DeploymentStatus):
        self.status = status

    def get_inactive_environment(self):
        if self.active_environment == "blue":
            return "green"

        return "blue"

    def deploy(
        self,
        image: str,
        deployment_id=None,
        db: Session = None,
        container_name: str = None,
        base_url: str = None
    ):
        self.set_status(DeploymentStatus.PENDING)

        # ---------------------------------
        # GET CURRENT ENVIRONMENT FROM DB
        # ---------------------------------
        previous_environment = self.active_environment

        if deployment_id is not None and db is not None:
            deployment = (
                db.query(Deployment)
                .filter(Deployment.id == deployment_id)
                .first()
            )

            if deployment is not None:
                application = (
                    db.query(Application)
                    .filter(Application.id == deployment.application_id)
                    .first()
                )

                if application is not None and application.active_environment:
                    previous_environment = application.active_environment
                    self.active_environment = previous_environment

        # ---------------------------------
        # DEPLOY TO INACTIVE ENVIRONMENT
        # ---------------------------------
        target_environment = self.get_inactive_environment()

        host_port = ENVIRONMENT_PORTS[target_environment]

        if deployment_id is not None and db is not None:
            deployment = (
                db.query(Deployment)
                .filter(Deployment.id == deployment_id)
                .first()
            )

            if deployment is not None:
                deployment.target_environment = target_environment
                db.commit()

        if container_name is None:
            container_name = f"{application.name}-{target_environment}"

        if base_url is None:
            base_url = f"http://localhost:{host_port}"

        container = None

        try:
            # -----------------------------
            # DEPLOYING
            # -----------------------------
            self.set_status(DeploymentStatus.DEPLOYING)
            if deployment_id is not None:
                self.update_deployment_status(
                    db,
                    deployment_id,
                    DeploymentStatus.DEPLOYING
                )

                deployment = (
                    db.query(Deployment)
                    .filter(Deployment.id == deployment_id)
                    .first()
                )

                if deployment is not None:
                    deployment.started_at = datetime.utcnow()
                    db.commit()
            self.docker_service.pull_image(image)

            container = self.docker_service.create_container(
                image=image,
                name=container_name,
                host_port=host_port
            )

            instance = None

            if deployment_id is not None:
                deployment = (
                    db.query(Deployment)
                    .filter(Deployment.id == deployment_id)
                    .first()
                )

                if deployment is not None:
                    instance = Instance(
                        application_id=deployment.application_id,
                        deployment_id=deployment.id,
                        environment=target_environment,
                        container_id=container.id,
                        container_name=container.name,
                        host_port=host_port,
                        container_port=8000,
                        status="created"
                    )

                    db.add(instance)
                    db.commit()
                    db.refresh(instance)

            self.docker_service.start_container(container)

            if deployment_id is not None and instance is not None:
                instance.status = "running"
                db.commit()
            # -----------------------------
            # HEALTH CHECK
            # -----------------------------
            self.set_status(DeploymentStatus.HEALTH_CHECK)
            if deployment_id is not None:
                self.update_deployment_status(
                    db,
                    deployment_id,
                    DeploymentStatus.HEALTH_CHECK
                )
            target_base_url = f"http://localhost:{host_port}"

            health_url = f"{target_base_url}/health"

            healthy = self.health_service.check(health_url)

            if not healthy:
                self.set_status(DeploymentStatus.FAILED)

                self.docker_service.stop_container(container)
                self.docker_service.remove_container(container)

                return {
                    "status": self.status.value,
                    "reason": "Health check failed",
                    "environment": target_environment
                }

            # -----------------------------
            # SMOKE TEST
            # -----------------------------
            self.set_status(DeploymentStatus.SMOKE_TEST)
            if deployment_id is not None:
                self.update_deployment_status(
                    db,
                    deployment_id,
                    DeploymentStatus.SMOKE_TEST
                )
            smoke_test_passed = self.smoke_test_service.run(
                target_base_url,
                ["/health", "/version"]
            )

            if not smoke_test_passed:
                self.set_status(DeploymentStatus.FAILED)

                self.docker_service.stop_container(container)
                self.docker_service.remove_container(container)

                return {
                    "status": self.status.value,
                    "reason": "Smoke test failed",
                    "environment": target_environment
                }

            # -----------------------------
            # SWITCH TRAFFIC
            # -----------------------------
            self.set_status(DeploymentStatus.SWITCHING)
            if deployment_id is not None:
                self.update_deployment_status(
                    db,
                    deployment_id,
                    DeploymentStatus.SWITCHING
                )
            self.nginx_service.switch_traffic(target_environment)


            self.active_environment = target_environment

            if deployment_id is not None:
                deployment = (
                    db.query(Deployment)
                    .filter(Deployment.id == deployment_id)
                    .first()
                )

                if deployment is not None:
                    application = (
                        db.query(Application)
                        .filter(Application.id == deployment.application_id)
                        .first()
                    )

                    if application is not None:
                        print("DEBUG BEFORE:")
                        print(application.current_version)
                        print(application.active_environment)
                        print(application.status)


                        application.active_environment = target_environment
                        application.current_version = deployment.version
                        application.status = "active"

                        print("DEBUG AFTER:")
                        print(application.current_version)
                        print(application.active_environment)
                        print(application.status)
                        db.commit()

            # -----------------------------
            # MONITORING
            # -----------------------------
            self.set_status(DeploymentStatus.MONITORING)
            if deployment_id is not None:
                self.update_deployment_status(
                    db,
                    deployment_id,
                    DeploymentStatus.MONITORING
                )
            # Monitoring will be supplied with
            # request statistics.
            #
            # For now these values are passed as
            # arguments to deploy().
            #
            # This keeps the service easy to test.
            return {
                "status": self.status.value,
                "environment": target_environment,
                "container": container.name,
                "previous_environment": previous_environment
            }

        except Exception as e:
            self.set_status(DeploymentStatus.FAILED)

            if deployment_id is not None and db is not None:
                deployment = (
                    db.query(Deployment)
                    .filter(Deployment.id == deployment_id)
                    .first()
                )

                if deployment is not None:
                    deployment.status = DeploymentStatus.FAILED.value
                    deployment.failure_reason = str(e)
                    deployment.completed_at = datetime.utcnow()
                    db.commit()

            if container is not None:
                try:
                    self.docker_service.stop_container(container)
                    self.docker_service.remove_container(container)
                except Exception:
                    pass

            raise
    def monitor(
        self,
        total_requests: int,
        failed_requests: int,
        failed_container,
        previous_base_url: str,
        deployment_id=None,
        db: Session = None
    ):
        """
        Evaluate the current deployment.

        If the error rate exceeds the configured
        threshold, automatically rollback.
        """

        self.set_status(DeploymentStatus.MONITORING)

        healthy = self.monitoring_service.is_healthy(
            total_requests=total_requests,
            failed_requests=failed_requests
        )

        if healthy:
            if deployment_id is not None:
                self.update_deployment_status(
                    db,
                    deployment_id,
                    DeploymentStatus.SUCCESS
                )

                deployment = (
                    db.query(Deployment)
                    .filter(Deployment.id == deployment_id)
                    .first()
                )

                if deployment is not None:
                    deployment.completed_at = datetime.utcnow()
                    db.commit()

            return {
                "status": self.status.value,
                "environment": self.active_environment
            }
        self.set_status(DeploymentStatus.ROLLING_BACK)
        # Deployment is unhealthy
        self.set_status(DeploymentStatus.ROLLING_BACK)

        previous_environment = self.get_inactive_environment()

        rollback_result = self.rollback_service.rollback(
            previous_environment=previous_environment,
            failed_container=failed_container,
            previous_base_url=previous_base_url
        )

        if rollback_result["status"] == "rolled_back":
            self.active_environment = previous_environment
            self.set_status(DeploymentStatus.ROLLED_BACK)

        if deployment_id is not None and db is not None:
            deployment = (
                db.query(Deployment)
                .filter(Deployment.id == deployment_id)
                .first()
            )
            if deployment is not None:
                deployment.status = DeploymentStatus.ROLLED_BACK.value
                deployment.completed_at = datetime.utcnow()

                instance = (
                    db.query(Instance)
                    .filter(Instance.deployment_id == deployment.id)
                    .first()
                )

                if instance is not None:
                    instance.status = "removed"
                application = (
                    db.query(Application)
                    .filter(
                        Application.id == deployment.application_id
                    )
                    .first()
                )

                if application is not None:
                    application.active_environment = previous_environment
                    application.status = "active"
                db.commit()
            return {
                "status": self.status.value,
                "environment": previous_environment,
                "reason": "Error rate exceeded threshold"
            }

        self.set_status(DeploymentStatus.FAILED)

        return {
            "status": self.status.value,
            "environment": self.active_environment,
            "reason": rollback_result["reason"]
        }

    def rollback(
        self,
        failed_container,
        previous_base_url: str
    ):
        """
        Manually roll back the current deployment.
        """

        self.set_status(DeploymentStatus.ROLLING_BACK)

        previous_environment = self.get_inactive_environment()

        result = self.rollback_service.rollback(
            previous_environment=previous_environment,
            failed_container=failed_container,
            previous_base_url=previous_base_url
        )

        if result["status"] == "rolled_back":
            self.active_environment = previous_environment
            self.set_status(DeploymentStatus.ROLLED_BACK)

            return {
                "status": self.status.value,
                "environment": previous_environment,
                "container": failed_container.name
            }

        self.set_status(DeploymentStatus.FAILED)

        return {
            "status": self.status.value,
            "reason": result["reason"],
            "environment": previous_environment
        }
    def update_deployment_status(
        self,
        db: Session,
        deployment_id,
        status: DeploymentStatus
    ):
        deployment = (
            db.query(Deployment)
            .filter(Deployment.id == deployment_id)
            .first()
        )

        if deployment is None:
            return

        deployment.status = status.value

        db.commit()