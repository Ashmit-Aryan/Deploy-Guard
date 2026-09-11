import os


BLUE_PORT = int(os.getenv("DEPLOYGUARD_BLUE_PORT", "8001"))
GREEN_PORT = int(os.getenv("DEPLOYGUARD_GREEN_PORT", "8002"))

ENVIRONMENT_PORTS = {
    "blue": BLUE_PORT,
    "green": GREEN_PORT,
}

NGINX_UPSTREAM_PATH = os.getenv(
    "DEPLOYGUARD_NGINX_UPSTREAM_PATH",
    "/etc/nginx/conf.d/deployguard-upstream.conf",
)
CONTAINER_SOCKET = os.getenv(
    "DEPLOYGUARD_CONTAINER_SOCKET",
    "unix:///run/user/1000/podman/podman.sock",
)
