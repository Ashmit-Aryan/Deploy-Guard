import subprocess
from pathlib import Path

from app.core.config import ENVIRONMENT_PORTS


class NginxService:

    def __init__(
        self,
        config_path: str = "/etc/nginx/conf.d/deployguard-upstream.conf"
    ):
        self.config_path = Path(config_path)

    def switch_traffic(self, environment: str):
        if environment not in ENVIRONMENT_PORTS:
            raise ValueError("Environment must be 'blue' or 'green'")

        port = ENVIRONMENT_PORTS[environment]

        config = (
            "upstream app_backend {\n"
            f"    server 127.0.0.1:{port};\n"
            "}\n"
        )

        self.config_path.write_text(config)

        if not self.test_config():
            raise RuntimeError("Nginx configuration test failed")

        self.reload()

    def test_config(self):
        result = subprocess.run(
            ["sudo", "nginx", "-t"],
            capture_output=True,
            text=True
        )

        return result.returncode == 0

    def reload(self):
        subprocess.run(
            ["sudo", "nginx", "-s", "reload"],
            check=True
        )