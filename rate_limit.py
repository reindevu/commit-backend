import time
from collections import defaultdict, deque
from threading import Lock
from typing import Deque

from fastapi import Request


class IpRateLimiter:
    # In-memory sliding window limiter by client IP.
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.events: dict[str, Deque[float]] = defaultdict(deque)
        self.lock = Lock()

    def check(self, key: str) -> int:
        now = time.time()
        cutoff = now - self.window_seconds

        with self.lock:
            bucket = self.events[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= self.max_requests:
                retry_after = int(self.window_seconds - (now - bucket[0]))
                return max(retry_after, 1)

            bucket.append(now)
            return 0


def get_client_ip(request: Request, trust_proxy: bool, trusted_proxies: set[str]) -> str:
    remote_ip = request.client.host if request.client else "unknown"
    if not trust_proxy:
        return remote_ip

    # Only trust forwarded headers from explicitly trusted proxy hosts.
    if remote_ip not in trusted_proxies:
        return remote_ip

    forwarded_for = request.headers.get("x-forwarded-for", "")
    if not forwarded_for:
        return remote_ip

    first_ip = forwarded_for.split(",")[0].strip()
    return first_ip or remote_ip
