from dataclasses import dataclass
import os

@dataclass
class AppConfig:
    api_base_url: str
    request_timeout_s: float = 10.0

    @staticmethod
    def load() -> "AppConfig":
        return AppConfig(
            api_base_url=os.getenv("API_BASE_URL", "http://127.0.0.1:8000"),
            request_timeout_s=float(os.getenv("API_TIMEOUT_S", "10"))
        )
