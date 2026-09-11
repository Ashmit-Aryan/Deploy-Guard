import docker # pyright: ignore[reportMissingModuleSource]

from app.core.config import CONTAINER_SOCKET


class DockerService:

    def __init__(self):
        self.client = docker.DockerClient(
            base_url=CONTAINER_SOCKET
        )

    def test_connection(self):
        return self.client.ping()

    def get_containers(self):
        return self.client.containers.list()

    def get_container(self, container_id_or_name: str):
        try:
            return self.client.containers.get(container_id_or_name)
        except docker.errors.NotFound: # pyright: ignore[reportAttributeAccessIssue]
            return None

    def pull_image(self, image_name: str):
        try:
            return self.client.images.get(image_name)
        except docker.errors.ImageNotFound: # pyright: ignore[reportAttributeAccessIssue]
            return self.client.images.pull(image_name)

    def create_container(self,image:str,name:str,host_port:int,container_port:int=8000):
        return self.client.containers.create(
            image=image,name=name,ports = {f"{container_port}/tcp":host_port}
        )
    
    def start_container(self, container):
        container.start()
        return container

    def stop_container(self, container):
        container.stop()
        return container

    def remove_container(self, container):
        container.remove(force=True)
