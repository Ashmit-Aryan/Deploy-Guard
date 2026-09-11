import time
import requests # pyright: ignore[reportMissingModuleSource]


class HealthService:

    def check(
        self,
        url: str,
        retries: int = 10,
        delay: float = 1.0
    ) -> bool:

        for _ in range(retries):
            try:
                response = requests.get(url, timeout=5)

                if response.status_code == 200:
                    return True

            except requests.RequestException:
                pass

            time.sleep(delay)

        return False