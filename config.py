import os

from dotenv import load_dotenv

load_dotenv()

RATE_LIMIT_MAX_REQUESTS = 3
RATE_LIMIT_WINDOW_SECONDS = 10 * 60


def parse_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_trusted_proxy_ips() -> set[str]:
    raw = os.getenv("TRUSTED_PROXY_IPS", "")
    return {item.strip() for item in raw.split(",") if item.strip()}


def parse_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [item.strip() for item in raw.split(",") if item.strip()]


PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_BASE_URL = os.getenv("PERPLEXITY_BASE_URL")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar")

TRUST_PROXY = parse_bool_env("TRUST_PROXY", default=False)
TRUSTED_PROXY_IPS = parse_trusted_proxy_ips()
CORS_ORIGINS = parse_cors_origins()
