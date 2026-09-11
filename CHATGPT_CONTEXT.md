# DeployGuard — ChatGPT Project Context

## What DeployGuard is

DeployGuard is a local-first, zero-downtime deployment platform for a hackathon MVP. It uses a **Blue-Green deployment** strategy:

```text
React dashboard → FastAPI control plane → deployment services
                                     ↓
                           Podman containers + Nginx
                                     ↓
                             Blue / Green application
```

PostgreSQL is the persistent source of truth for application, deployment, and instance state.

The authoritative architecture roadmap is `MVP - Tech Specs.md`. Do not introduce Kubernetes, microservices, Redis, Celery, Kafka, AWS, Terraform, CI/CD, Prometheus, or Grafana until the local MVP and frontend integration are complete.

## Local environment

- OS: Fedora
- Python: 3.14
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL
- Container runtime: Podman, accessed via the Python Docker SDK
- Reverse proxy: host-managed Nginx
- Frontend: React + Vite + Tailwind

Important local endpoints:

| Purpose | Address |
| --- | --- |
| React development server | `http://localhost:5173` |
| FastAPI control plane | `http://localhost:8000` |
| Public deployed application via Nginx | `http://localhost` |
| Blue app host port | `8001` |
| Green app host port | `8002` |

Podman socket:

```text
unix:///run/user/1000/podman/podman.sock
```

Nginx upstream file:

```text
/etc/nginx/conf.d/deployguard-upstream.conf
```

The upstream must point to `127.0.0.1:8001` for Blue or `127.0.0.1:8002` for Green. Nginx reloads, rather than restarts, when traffic changes.

## Database

Local connection string:

```text
postgresql+psycopg2://deployguard:deployguard@localhost:5432/deployguard
```

Core tables:

- `applications`: application metadata, current version, active environment, and status.
- `deployments`: requested image/version, target environment, lifecycle status, timings, and failure reason.
- `instances`: container identity, environment, mapped ports, and runtime lifecycle state.

Current demo application:

```text
ID:      36a84dd2-4ab8-4367-9bf8-2572bcbbe3bf
Name:    deployguard-demo
Image:   deployguard-demo:v2
Version: 2.0.0
```

At the latest verified state, Blue is active, version `2.0.0`, and Green has been removed after rollback.

## Core deployment flow

The public deployment API is:

```http
POST /api/applications/{application_id}/deploy
```

Example request body:

```json
{
  "version": "2.0.0",
  "image": "deployguard-demo:v2"
}
```

The endpoint creates a `Deployment` record and starts a FastAPI background task. The background task creates its **own** `SessionLocal()` database session; it must never receive a request-scoped SQLAlchemy session.

Deployment algorithm:

```text
Read Application.active_environment from PostgreSQL
→ choose the inactive Blue/Green environment
→ record target environment
→ pull image
→ create Instance record
→ create and start Podman container
→ health check: GET /health
→ smoke test: GET /health and GET /version
→ update Nginx upstream and reload Nginx
→ update Application state
→ set Deployment status to monitoring
```

Lifecycle states:

```text
pending → deploying → health_check → smoke_test → switching → monitoring
                                                          ↓
                                                    success

monitoring → rolling_back → rolled_back
```

On a health/smoke/container failure, the deployment records `failed`, its actual failure reason, and its completion time. Any created instance is marked `removed` after its container is removed.

## Monitoring and automatic rollback

The current MVP monitoring endpoint is:

```http
POST /api/monitor?total_requests=100&failed_requests=10&deployment_id={id}
```

The error threshold is 5%. If the error rate exceeds it, DeployGuard:

```text
switches Nginx to the previous environment
→ verifies the previous environment's /health endpoint
→ removes the failed container
→ marks its Instance as removed
→ marks the Deployment as rolled_back
→ restores Application.active_environment and status
```

When restoring `Application.current_version`, use a previous successful deployment record from PostgreSQL. Do not invent a version.

## APIs currently present

```text
GET    /health
GET    /api/db-test

GET    /api/applications
POST   /api/applications
GET    /api/applications/{id}
DELETE /api/applications/{id}

POST   /api/applications/{id}/deploy
POST   /api/applications/{id}/rollback
GET    /api/applications/{id}/deployments
GET    /api/deployments/{deployment_id}
POST   /api/monitor
```

Legacy generic routes (`/api/deploy`, `/api/rollback`, and `/deploy-test`) were deliberately removed. Do not reintroduce endpoints that accept a container name, host port, target environment, or base URL from the client. Those values belong to the service/configuration layers.

## Verified live scenario

The following was verified against the real local Podman, Nginx, and PostgreSQL setup:

1. Restored Blue as the baseline.
2. Created deployment `eafc97f1-6b1f-4cef-8416-7edc3ee6ff16` targeting Green.
3. Green passed health and smoke validation and reached `monitoring`.
4. Monitoring with 100 requests and 0 failures returned `success`.
5. Monitoring with 100 requests and 10 failures triggered automatic rollback.
6. Final persisted state was:

```text
Application: Blue / active / version 2.0.0
Deployment:  rolled_back
Reason:      Error rate exceeded threshold
Green instance: removed
```

## Code layout

```text
backend/app/
├── main.py                         # Thin FastAPI routes
├── core/config.py                  # Ports, socket, Nginx path
├── core/database.py                # SQLAlchemy engine/session/base
├── models/                         # Application, Deployment, Instance
├── schemas/                        # API request schemas
└── services/
    ├── deployment_service.py       # Deployment orchestration
    ├── docker_service.py           # Podman via Docker SDK
    ├── nginx_service.py            # Upstream write/test/reload
    ├── health_service.py
    ├── smoke_test_service.py
    ├── monitoring_service.py
    └── rollback_service.py

frontend/src/
├── components/                     # Small, componentized UI pieces
├── pages/Dashboard.jsx
├── hooks/useDeployment.js          # Deployment polling
└── services/api.js                 # Application-scoped API calls
```

## Frontend state and next priority

The frontend uses the application-scoped deployment API and polls deployment status. It currently asks for an application UUID in the deploy form; this is functional but not the desired final UX. The backend now also has application-scoped deployment history and manual rollback APIs.

The next task is frontend integration, in this order:

1. Fetch and display registered applications.
2. Let the user select an application instead of entering a UUID.
3. Add deployment history per application.
4. Show deployment lifecycle, success, failure, and rollback information clearly.
5. Add a manual rollback control that calls the existing application-scoped rollback API and displays any conflict/error state.

## Working rules

- Follow `MVP - Tech Specs.md` and keep the MVP local-first.
- Inspect existing code before changing it.
- Make small changes, then test and verify each one.
- Keep API routes thin; deployment/infrastructure behavior belongs in services.
- Keep PostgreSQL records authoritative for persistent deployment state.
- Do not hardcode `deployguard-demo`, container names, Blue/Green ports, or environment choices in API routes.
- Preserve the known-working Podman and host Nginx arrangement.
