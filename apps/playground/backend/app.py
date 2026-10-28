"""Optional FastAPI browser adapter; does not change the SDK or CLI.

Run locally with: uv run --extra playground python -m apps.playground.backend
"""

from __future__ import annotations

import hmac
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from applied_ai.core.exceptions import LLMError

from .service import COMPARISONS, EXAMPLES, compare, discover_patterns, execute

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"


@dataclass(frozen=True)
class PlaygroundConfig:
    """Token and explicit live authorization are server-only settings."""

    token: str | None = None
    enable_live: bool = False
    max_units: int = 80
    concurrency: int = 2

    def __post_init__(self) -> None:
        if self.enable_live and (not self.token or len(self.token) < 16):
            raise ValueError("Live playground requires PLAYGROUND_TOKEN of >=16 characters")
        if not 1 <= self.max_units <= 1000:
            raise ValueError("max_units must be between 1 and 1000")
        if not 1 <= self.concurrency <= 8:
            raise ValueError("concurrency must be between 1 and 8")


class RunInput(BaseModel):
    example_id: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=500)
    live: bool = False


class CompareInput(BaseModel):
    comparison_id: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=500)


class Quota:
    """Atomic process-local budget; restarting server resets it."""

    def __init__(self, max_units: int, concurrency: int) -> None:
        self.max_units = max_units
        self.used = 0
        self._lock = threading.Lock()
        self._semaphore = threading.BoundedSemaphore(concurrency)

    def acquire(self, cost: int) -> None:
        if not self._semaphore.acquire(blocking=False):
            raise HTTPException(429, detail="Playground concurrency limit reached")
        with self._lock:
            if self.used + cost > self.max_units:
                self._semaphore.release()
                raise HTTPException(429, detail="Playground session budget exhausted")
            self.used += cost

    def release(self) -> None:
        self._semaphore.release()

    def status(self) -> dict[str, int]:
        with self._lock:
            return {
                "used": self.used,
                "limit": self.max_units,
                "remaining": self.max_units - self.used,
            }


def create_app(config: PlaygroundConfig | None = None) -> FastAPI:
    if config is None:
        config = PlaygroundConfig(token=os.getenv("PLAYGROUND_TOKEN") or None)
    quota = Quota(config.max_units, config.concurrency)
    app = FastAPI(
        title="Applied AI Lab Playground", docs_url=None, redoc_url=None, openapi_url=None
    )
    app.state.playground_quota = quota
    app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

    @app.middleware("http")
    async def security_headers(request: Request, call_next: Any) -> Any:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; font-src 'self'; "
            "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
        )
        return response

    def require_auth(request: Request) -> None:
        if config.token is None and (
            request.client is None
            or request.client.host not in {"127.0.0.1", "::1", "localhost", "testclient"}
        ):
            raise HTTPException(
                403, detail="Tokenless API access is restricted to loopback clients"
            )
        if config.token is not None:
            authorization = request.headers.get("Authorization", "")
            if not authorization.startswith("Bearer ") or not hmac.compare_digest(
                authorization.removeprefix("Bearer "), config.token
            ):
                raise HTTPException(401, detail="Playground access token required")
        if request.method in {"POST", "PUT", "DELETE", "PATCH"}:
            origin = request.headers.get("origin")
            if origin is not None:
                # Reject cross-site requests; same-origin front-end is supported.
                expected = f"{request.url.scheme}://{request.headers.get('host', '')}"
                if origin != expected:
                    raise HTTPException(403, detail="Cross-origin writes are disabled")
            elif config.token is None:
                # Browser writes require Origin if token auth is not in use.
                # CLI / same-machine Python clients should configure a token.
                raise HTTPException(403, detail="Origin required without API token")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(FRONTEND / "index.html")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/settings")
    def settings(_auth: None = Depends(require_auth)) -> dict[str, Any]:
        return {
            "mode": "local-playground",
            "live_enabled": config.enable_live,
            "auth_required": config.token is not None,
            "sandbox_enabled": False,
            "quotas": quota.status(),
        }

    @app.get("/api/catalog")
    def catalog(_auth: None = Depends(require_auth)) -> dict[str, Any]:
        return {
            "patterns": discover_patterns(),
            "examples": [e.__dict__ for e in EXAMPLES],
            "comparisons": list(COMPARISONS),
        }

    @app.post("/api/run")
    def run(payload: RunInput, _auth: None = Depends(require_auth)) -> dict[str, Any]:
        if payload.live and not config.enable_live:
            raise HTTPException(403, detail="Live providers disabled; restart with explicit opt-in")
        quota.acquire(1)
        try:
            return {
                "result": execute(payload.example_id, payload.value, live=payload.live),
                "quota": quota.status(),
            }
        except (ValueError, LookupError) as exc:
            raise HTTPException(400, detail=str(exc)) from exc
        except LLMError as exc:
            raise HTTPException(
                502, detail={"category": exc.category, "message": "Provider operation failed"}
            ) from exc
        finally:
            quota.release()

    @app.post("/api/compare")
    def comparisons(payload: CompareInput, _auth: None = Depends(require_auth)) -> dict[str, Any]:
        quota.acquire(2)
        try:
            return {
                "result": compare(payload.comparison_id, payload.value),
                "quota": quota.status(),
            }
        except ValueError as exc:
            raise HTTPException(400, detail=str(exc)) from exc
        finally:
            quota.release()

    return app


app = create_app()
