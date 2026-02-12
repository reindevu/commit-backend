from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from config import (
    CORS_ORIGINS,
    RATE_LIMIT_MAX_REQUESTS,
    RATE_LIMIT_WINDOW_SECONDS,
    TRUST_PROXY,
    TRUSTED_PROXY_IPS,
)
from llm import generate_suggestions
from rate_limit import IpRateLimiter, get_client_ip
from schemas import SuggestItem, SuggestRequest

limiter = IpRateLimiter(max_requests=RATE_LIMIT_MAX_REQUESTS, window_seconds=RATE_LIMIT_WINDOW_SECONDS)

app = FastAPI(title="Commit Branch Suggester API",root_path="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/suggest", response_model=list[SuggestItem])
def suggest(payload: SuggestRequest, request: Request) -> list[SuggestItem]:
    ip = get_client_ip(request, trust_proxy=TRUST_PROXY, trusted_proxies=TRUSTED_PROXY_IPS)
    retry_after = limiter.check(ip)
    if retry_after > 0:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_MAX_REQUESTS} requests per 10 minutes per IP.",
            headers={"Retry-After": str(retry_after)},
        )

    try:
        return generate_suggestions(payload.text)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        print(exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
