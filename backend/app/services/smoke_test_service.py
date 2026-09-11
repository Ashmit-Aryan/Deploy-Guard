import requests # pyright: ignore[reportMissingModuleSource, reportAttributeAccessIssue]


class SmokeTestService:

    def check_endpoint(self, url: str) -> bool:
        try:
            response = requests.get(url, timeout=5)
            return 200 <= response.status_code < 300
        except requests.RequestException:
            return False

    def run(self, base_url: str, endpoints: list[str]) -> bool:
        for endpoint in endpoints:
            url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

            if not self.check_endpoint(url):
                return False

        return True