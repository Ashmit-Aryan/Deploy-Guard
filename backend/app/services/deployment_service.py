from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import ENVIRONMENT_PORTS
from app.core.database import SessionLocal
from app.models.application import Application
from app.models.deployment import Deployment
from app.models.instance import Instance
from app.services.deployment_status import DeploymentStatus
from app.services.docker_service import DockerService
from app.services.health_service import HealthService
from app.services.monitoring_service import MonitoringService
from app.services.nginx_service import NginxService
from app.services.rollback_service import RollbackService
from app.services.smoke_test_service import SmokeTestService


class DeploymentService:
    """Orchestrates database-backed Blue-Green deployments."""

    def __init__(self):
        self.docker_service = DockerService()
        self.nginx_service = NginxService()
        self.health_service = HealthService()
        self.smoke_test_service = SmokeTestService()
        self.rollback_service = RollbackService()
        self.monitoring_service = MonitoringService()
        # Compatibility state for legacy callers. Application.active_environment
        # is authoritative whenever a database deployment is used.
        self.active_environment = "blue"
        self.status = DeploymentStatus.PENDING

    def set_status(self, status: DeploymentStatus):
        self.status = status

    def get_inactive_environment(self, active_environment: str | None = None):
        return "green" if (active_environment or self.active_environment) == "blue" else "blue"

    def deploy_by_id(self, deployment_id):
        """Background entry point: never reuse the HTTP request session."""
        db = SessionLocal()
        try:
            deployment = db.get(Deployment, deployment_id)
            if deployment is not None:
                self.deploy(image=deployment.image, deployment_id=deployment.id, db=db)
        finally:
            db.close()

    def update_deployment_status(self, db: Session | None, deployment_id, status: DeploymentStatus):
        self.set_status(status)
        if db is None or deployment_id is None:
            return
        deployment = db.get(Deployment, deployment_id)
        if deployment is not None:
            deployment.status = status.value
            db.commit()

    def _fail_deployment(self, db: Session | None, deployment_id, reason: str, instance=None):
        self.set_status(DeploymentStatus.FAILED)
        if db is None or deployment_id is None:
            return
        deployment = db.get(Deployment, deployment_id)
        if deployment is not None:
            deployment.status = DeploymentStatus.FAILED.value
            deployment.failure_reason = reason
            deployment.completed_at = datetime.utcnow()
        if instance is not None:
            instance.status = "removed"
        db.commit()

    def _remove_inactive_instances(
        self,
        db: Session,
        application: Application,
        environment: str,
    ):
        """Free the inactive slot before its fixed container name is reused."""
        instances = (
            db.query(Instance)
            .filter(
                Instance.application_id == application.id,
                Instance.environment == environment,
                Instance.status.in_(["created", "running"]),
            )
            .all()
        )

        known_container_ids = set()
        for instance in instances:
            known_container_ids.add(instance.container_id)
            container = self.docker_service.get_container(
                instance.container_id or instance.container_name
            )
            if container is not None:
                self.docker_service.stop_container(container)
                self.docker_service.remove_container(container)
            instance.status = "removed"

        if instances:
            db.commit()

        # Older local baselines may have a container without an Instance row.
        # The name is derived from application metadata and the inactive target,
        # not supplied by an API client.
        container = self.docker_service.get_container(
            f"{application.name}-{environment}"
        )
        if container is not None and container.id not in known_container_ids:
            self.docker_service.stop_container(container)
            self.docker_service.remove_container(container)

    def _complete_rollback(
        self,
        db: Session,
        application: Application,
        failed_instance: Instance,
        previous_environment: str,
        reason: str,
    ):
        """Persist rollback state after Nginx and health verification succeed."""
        failed_instance.status = "removed"
        deployment = (
            db.get(Deployment, failed_instance.deployment_id)
            if failed_instance.deployment_id is not None
            else None
        )
        previous_deployment = (
            db.query(Deployment)
            .filter(
                Deployment.application_id == application.id,
                Deployment.target_environment == previous_environment,
                Deployment.status == DeploymentStatus.SUCCESS.value,
            )
            .order_by(Deployment.completed_at.desc())
            .first()
        )

        application.active_environment = previous_environment
        application.status = "active"
        if previous_deployment is not None:
            application.current_version = previous_deployment.version

        if deployment is not None:
            deployment.status = DeploymentStatus.ROLLED_BACK.value
            deployment.failure_reason = reason
            deployment.completed_at = datetime.utcnow()

        self.active_environment = previous_environment
        self.set_status(DeploymentStatus.ROLLED_BACK)
        db.commit()

    def deploy(self, image: str, deployment_id=None, db: Session | None = None,
               container_name: str | None = None, base_url: str | None = None):
        deployment = None
        application = None
        instance = None
        container = None
        previous_environment = self.active_environment

        if deployment_id is not None and db is not None:
            deployment = db.get(Deployment, deployment_id)
            if deployment is None:
                raise ValueError("Deployment not found")
            application = db.get(Application, deployment.application_id)
            if application is None:
                raise ValueError("Application not found")
            previous_environment = application.active_environment or "blue"
            self.active_environment = previous_environment

        target_environment = self.get_inactive_environment(previous_environment)
        host_port = ENVIRONMENT_PORTS[target_environment]
        container_name = container_name or f"{application.name if application else 'deployguard'}-{target_environment}"
        target_base_url = base_url or f"http://localhost:{host_port}"

        if deployment is not None:
            deployment.target_environment = target_environment
            db.commit()

        try:
            self.update_deployment_status(db, deployment_id, DeploymentStatus.DEPLOYING)
            if deployment is not None:
                deployment.started_at = datetime.utcnow()
                db.commit()
                self._remove_inactive_instances(
                    db,
                    application,
                    target_environment,
                )

            self.docker_service.pull_image(image)
            container = self.docker_service.create_container(
                image=image, name=container_name, host_port=host_port
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
                    status="created",
                )
                db.add(instance)
                db.commit()

            self.docker_service.start_container(container)
            if instance is not None:
                instance.status = "running"
                db.commit()

            self.update_deployment_status(db, deployment_id, DeploymentStatus.HEALTH_CHECK)
            if not self.health_service.check(f"{target_base_url}/health"):
                self.docker_service.stop_container(container)
                self.docker_service.remove_container(container)
                self._fail_deployment(db, deployment_id, "Health check failed", instance)
                return {"status": "failed", "reason": "Health check failed", "environment": target_environment}

            self.update_deployment_status(db, deployment_id, DeploymentStatus.SMOKE_TEST)
            if not self.smoke_test_service.run(target_base_url, ["/health", "/version"]):
                self.docker_service.stop_container(container)
                self.docker_service.remove_container(container)
                self._fail_deployment(db, deployment_id, "Smoke test failed", instance)
                return {"status": "failed", "reason": "Smoke test failed", "environment": target_environment}

            self.update_deployment_status(db, deployment_id, DeploymentStatus.SWITCHING)
            self.nginx_service.switch_traffic(target_environment)
            self.active_environment = target_environment
            if application is not None:
                application.active_environment = target_environment
                application.current_version = deployment.version
                application.status = "active"
                db.commit()

            self.update_deployment_status(db, deployment_id, DeploymentStatus.MONITORING)
            return {"status": "monitoring", "environment": target_environment,
                    "container": container.name, "previous_environment": previous_environment}
        except Exception as exc:
            if container is not None:
                try:
                    self.docker_service.stop_container(container)
                    self.docker_service.remove_container(container)
                except Exception:
                    pass
            self._fail_deployment(db, deployment_id, str(exc), instance)
            raise

    def monitor(self, total_requests: int, failed_requests: int, failed_container,
                previous_base_url: str, deployment_id=None, db: Session | None = None):
        self.set_status(DeploymentStatus.MONITORING)
        if self.monitoring_service.is_healthy(total_requests, failed_requests):
            self.update_deployment_status(db, deployment_id, DeploymentStatus.SUCCESS)
            if db is not None and deployment_id is not None:
                deployment = db.get(Deployment, deployment_id)
                if deployment is not None:
                    deployment.completed_at = datetime.utcnow()
                    db.commit()
            return {"status": "success", "environment": self.active_environment}

        deployment = db.get(Deployment, deployment_id) if db is not None and deployment_id else None
        active_environment = deployment.target_environment if deployment is not None else self.active_environment
        previous_environment = self.get_inactive_environment(active_environment)
        self.set_status(DeploymentStatus.ROLLING_BACK)
        result = self.rollback_service.rollback(previous_environment, failed_container, previous_base_url)
        if result["status"] != "rolled_back":
            self._fail_deployment(db, deployment_id, result.get("reason", "Rollback failed"))
            return {"status": "failed", "environment": self.active_environment,
                    "reason": result.get("reason", "Rollback failed")}

        if deployment is not None:
            instance = db.query(Instance).filter(Instance.deployment_id == deployment.id).first()
            application = db.get(Application, deployment.application_id)
            if instance is not None and application is not None:
                self._complete_rollback(
                    db,
                    application,
                    instance,
                    previous_environment,
                    "Error rate exceeded threshold",
                )

        return {"status": "rolled_back", "environment": previous_environment,
                "reason": "Error rate exceeded threshold"}

    def rollback(self, failed_container, previous_base_url: str):
        """Compatibility wrapper for service tests and temporary legacy callers."""
        self.set_status(DeploymentStatus.ROLLING_BACK)
        previous_environment = self.get_inactive_environment()
        result = self.rollback_service.rollback(previous_environment, failed_container, previous_base_url)
        if result["status"] == "rolled_back":
            self.active_environment = previous_environment
            self.set_status(DeploymentStatus.ROLLED_BACK)
            return {"status": "rolled_back", "environment": previous_environment,
                    "container": failed_container.name}
        self.set_status(DeploymentStatus.FAILED)
        return {"status": "failed", "environment": previous_environment,
                "reason": result.get("reason", "Rollback failed")}

    def rollback_application(self, application_id, db: Session):
        """Manually roll back an application's active instance using DB state."""
        application = db.get(Application, application_id)
        if application is None:
            raise LookupError("Application not found")
        if application.active_environment not in ENVIRONMENT_PORTS:
            raise ValueError("Application has no active environment to roll back")

        active_instance = (
            db.query(Instance)
            .filter(
                Instance.application_id == application.id,
                Instance.environment == application.active_environment,
                Instance.status == "running",
            )
            .order_by(Instance.created_at.desc())
            .first()
        )
        if active_instance is None:
            raise ValueError("Active running instance not found")

        previous_environment = self.get_inactive_environment(application.active_environment)
        previous_instance = (
            db.query(Instance)
            .filter(
                Instance.application_id == application.id,
                Instance.environment == previous_environment,
                Instance.status == "running",
            )
            .order_by(Instance.created_at.desc())
            .first()
        )
        if previous_instance is None:
            raise ValueError("Previous running instance not found")

        failed_container = self.docker_service.get_container(
            active_instance.container_id or active_instance.container_name
        )
        if failed_container is None:
            raise ValueError("Active deployment container not found")

        self.set_status(DeploymentStatus.ROLLING_BACK)
        result = self.rollback_service.rollback(
            previous_environment=previous_environment,
            failed_container=failed_container,
            previous_base_url=f"http://localhost:{previous_instance.host_port}",
        )
        if result["status"] != "rolled_back":
            self.set_status(DeploymentStatus.FAILED)
            raise RuntimeError(result.get("reason", "Rollback failed"))

        self._complete_rollback(
            db,
            application,
            active_instance,
            previous_environment,
            "Manual rollback requested",
        )
        return {
            "status": "rolled_back",
            "environment": previous_environment,
            "reason": "Manual rollback requested",
        }
