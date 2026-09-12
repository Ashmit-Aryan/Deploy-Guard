from app.models.deployment import Deployment
from app.models.instance import Instance
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException # pyright: ignore[reportMissingImports, reportMissingModuleSource]
from app.services.deployment_service import DeploymentService
from fastapi.middleware.cors import CORSMiddleware # pyright: ignore[reportMissingImports, reportMissingModuleSource]
from sqlalchemy.orm import Session
from app.schemas.deployment import DeploymentCreate
from app.core.database import Base, engine, get_db
from app.models.application import Application
from app.schemas.application import ApplicationCreate
from app.core.config import DEPLOYGUARD_WEBHOOK_SECRET
from fastapi import Header
from app.schemas.webhook import GitHubDeploymentWebhook
from app.core.database import SessionLocal


def run_deployment_background(
    deployment_id,
    image: str
):
    db = SessionLocal()

    try:
        deployment_service.deploy(
            image=image,
            deployment_id=deployment_id,
            db=db
        )
    finally:
        db.close()

app = FastAPI(
    title="DeployGuard API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
deployment_service = DeploymentService()


@app.on_event("startup")
def create_database_tables():
    """Create MVP tables locally; production should replace this with migrations."""
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "name": "DeployGuard",
        "message": "Zero-Downtime Deployment Platform"
    }

@app.get("/api/db-test")
def database_test(db: Session = Depends(get_db)):
    return {
        "database": "connected"
    }
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "DeployGuard API"
    }

@app.get("/api/applications")
def list_applications(
    db: Session = Depends(get_db)
):
    applications = db.query(Application).all()

    return [
        {
            "id": str(application.id),
            "name": application.name,
            "repository_url": application.repository_url,
            "image_repository": application.image_repository,
            "current_version": application.current_version,
            "active_environment": application.active_environment,
            "status": application.status,
        }
        for application in applications
    ]
@app.post("/api/applications")
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    new_application = Application(
        name=application.name,
        repository_url=application.repository_url,
        image_repository=application.image_repository,
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return {
        "id": str(new_application.id),
        "name": new_application.name,
        "repository_url": new_application.repository_url,
        "image_repository": new_application.image_repository,
        "status": new_application.status,
    }

@app.post("/api/monitor")
def monitor(
    total_requests: int,
    failed_requests: int,
    deployment_id: str,
    db: Session = Depends(get_db)
):
    # Find the deployment being monitored
    current_deployment = (
        db.query(Deployment)
        .filter(Deployment.id == deployment_id)
        .first()
    )

    if current_deployment is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )

    # Find the instance created for this deployment
    current_instance = (
        db.query(Instance)
        .filter(
            Instance.deployment_id == current_deployment.id
        )
        .first()
    )

    if current_instance is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment instance not found"
        )

    # Get the actual Docker container
    try:
        failed_container = (
            deployment_service.docker_service.client
            .containers
            .get(current_instance.container_id)
        )
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Deployment container not found"
        )

    # The previous environment is the opposite of
    # the deployment's target environment.
    previous_environment = (
        "green"
        if current_deployment.target_environment == "blue"
        else "blue"
    )

    # Use the instance record for the previous
    # environment to determine its actual port.
    previous_instance = (
        db.query(Instance)
        .filter(
            Instance.application_id == current_deployment.application_id,
            Instance.environment == previous_environment,
            Instance.status == "running"
        )
        .order_by(Instance.created_at.desc())
        .first()
    )

    if previous_instance is None:
        raise HTTPException(
            status_code=404,
            detail="Previous running instance not found"
        )

    previous_base_url = (
        f"http://localhost:{previous_instance.host_port}"
    )

    return deployment_service.monitor(
        total_requests=total_requests,
        failed_requests=failed_requests,
        failed_container=failed_container,
        previous_base_url=previous_base_url,
        deployment_id=deployment_id,
        db=db
    )

@app.get("/api/applications/{application_id}")
def get_application(
    application_id: str,
    db: Session = Depends(get_db)
):
    application = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return {
        "id": str(application.id),
        "name": application.name,
        "repository_url": application.repository_url,
        "image_repository": application.image_repository,
        "current_version": application.current_version,
        "active_environment": application.active_environment,
        "status": application.status,
    }


@app.get("/api/applications/{application_id}/deployments")
def list_application_deployments(
    application_id: str,
    db: Session = Depends(get_db),
):
    application = db.get(Application, application_id)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    deployments = (
        db.query(Deployment)
        .filter(Deployment.application_id == application.id)
        .order_by(Deployment.created_at.desc())
        .all()
    )

    return [
        {
            "deployment_id": str(deployment.id),
            "application_id": str(deployment.application_id),
            "version": deployment.version,
            "image": deployment.image,
            "target_environment": deployment.target_environment,
            "strategy": deployment.strategy,
            "status": deployment.status,
            "failure_reason": deployment.failure_reason,
            "started_at": deployment.started_at,
            "completed_at": deployment.completed_at,
            "created_at": deployment.created_at,
        }
        for deployment in deployments
    ]


@app.delete("/api/applications/{application_id}")
def delete_application(
    application_id: str,
    db: Session = Depends(get_db)
):
    application = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    db.delete(application)
    db.commit()

    return {
        "message": "Application deleted successfully",
        "id": application_id
    }

@app.post("/api/applications/{application_id}/deploy")
def create_deployment(
    application_id: str,
    deployment: DeploymentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    application = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    new_deployment = Deployment(
        application_id=application.id,
        version=deployment.version,
        image=deployment.image,
        target_environment=None,
        strategy="blue_green",
        status="pending"
    )

    db.add(new_deployment)
    db.commit()
    db.refresh(new_deployment)

    background_tasks.add_task(
        deployment_service.deploy_by_id,
        new_deployment.id,
    )

    return {
        "deployment_id": str(new_deployment.id),
        "status": "deploying"
    }


@app.post("/api/applications/{application_id}/rollback")
def rollback_application(
    application_id: str,
    db: Session = Depends(get_db),
):
    try:
        return deployment_service.rollback_application(application_id, db)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.get("/api/deployments/{deployment_id}")
def get_deployment_status(
    deployment_id: str,
    db: Session = Depends(get_db)
):
    deployment = (
        db.query(Deployment)
        .filter(Deployment.id == deployment_id)
        .first()
    )

    if deployment is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )

    return {
        "deployment_id": str(deployment.id),
        "application_id": str(deployment.application_id),
        "version": deployment.version,
        "image": deployment.image,
        "target_environment": deployment.target_environment,
        "strategy": deployment.strategy,
        "status": deployment.status,
        "failure_reason": deployment.failure_reason,
        "started_at": deployment.started_at,
        "completed_at": deployment.completed_at,
    }

@app.post("/api/webhooks/github")
def github_webhook(
    payload: GitHubDeploymentWebhook,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_deployguard_secret: str | None = Header(
        default=None,
        alias="X-DeployGuard-Secret"
    )
):
    if (
        not DEPLOYGUARD_WEBHOOK_SECRET
        or x_deployguard_secret != DEPLOYGUARD_WEBHOOK_SECRET
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook secret"
        )
    application = (
        db.query(Application)
        .filter(
            Application.id == payload.application_id
        )
        .first()
    )
    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    new_deployment = Deployment(
        application_id=application.id,
        version=payload.version,
        image=payload.image,
        commit_sha=payload.commit_sha,
        strategy="blue_green",
        status="pending"
    )

    db.add(new_deployment)
    db.commit()
    db.refresh(new_deployment)

    background_tasks.add_task(
        run_deployment_background,
        new_deployment.id,
        payload.image
    )

    return {
        "deployment_id": str(new_deployment.id),
        "application_id": str(application.id),
        "version": payload.version,
        "image": payload.image,
        "status": "deploying"
    }