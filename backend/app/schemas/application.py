from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    name: str
    repository_url: str
    image_repository: str