from pydantic import BaseModel, Field


class GitHubDeploymentWebhook(BaseModel):
    application_id: str = Field(
        ...,
        description="DeployGuard application UUID"
    )

    version: str = Field(
        ...,
        description="Release version or commit identifier"
    )

    image: str = Field(
        ...,
        description="GHCR Docker image reference"
    )

    commit_sha: str | None = Field(
        default=None,
        description="Git commit SHA that produced the image"
    )