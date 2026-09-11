from pydantic import BaseModel


class DeploymentCreate(BaseModel):
    version: str
    image: str