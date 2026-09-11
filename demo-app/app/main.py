from fastapi import FastAPI # pyright: ignore[reportMissingImports, reportAttributeAccessIssue]
from prometheus_fastapi_instrumentator import Instrumentator # pyright: ignore[reportMissingImports, reportAttributeAccessIssue]


app = FastAPI(
    title="DeployGuard Demo Application",
    version="2.0.0"
)


@app.get("/")
def root():
    return {
        "message": "DeployGuard Demo Application",
        "version": "2.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/version")
def version():
    return {
        "version": "2.0.0"
    }


# Prometheus instrumentation
Instrumentator().instrument(app).expose(app)