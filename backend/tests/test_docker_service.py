from app.services.docker_service import DockerService


def test_docker_connection():
    docker_service = DockerService()

    assert docker_service.test_connection() is True


def test_pull_image():
    docker_service = DockerService()

    image = docker_service.pull_image("nginx:alpine")

    assert image is not None


def test_create_and_start_container():
    docker_service = DockerService()

    container_name = "deployguard-test"

    # Remove old test container if it exists
    try:
        old_container = docker_service.client.containers.get(container_name)
        old_container.remove(force=True)
    except Exception:
        pass

    container = docker_service.create_container(
        image="nginx:alpine",
        name=container_name,
        host_port=8081,
        container_port=80
    )

    assert container is not None

    docker_service.start_container(container)

    container.reload()

    assert container.status == "running"

    container.remove(force=True)