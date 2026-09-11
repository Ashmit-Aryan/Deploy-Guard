from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI(
    title="DeployGuard Demo Application",
    version="3.0.0"
)


@app.get("/")
def root():
    return {
        "message": "DeployGuard Demo Application",
        "version": "3.0.0"
    }


@app.get("/health")
def health():
    # Deliberately healthy so deployment passes
    # the health check and reaches monitoring.
    return {
        "status": "healthy"
    }


@app.get("/version")
def version():
    return {
        "version": "3.0.0"
    }


@app.get("/api/demo")
def buggy_endpoint():
    # Deliberately broken endpoint.
    # This is used to generate 5xx errors during
    # the automatic rollback demonstration.
    raise HTTPException(
        status_code=500,
        detail="Intentional v3 application failure"
    )


# Prometheus instrumentation
Instrumentator().instrument(app).expose(app)
