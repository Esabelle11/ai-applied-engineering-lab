"""CLI runner for the optional localhost-only playground server."""

from __future__ import annotations

import argparse
import os

import uvicorn

from .app import PlaygroundConfig, create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local Applied AI playground")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--allow-live", action="store_true")
    parser.add_argument("--max-units", type=int, default=80)
    args = parser.parse_args()
    token = os.getenv("PLAYGROUND_TOKEN") or None
    if args.host not in {"127.0.0.1", "localhost", "::1"} and not token:
        parser.error("Non-loopback binding requires PLAYGROUND_TOKEN")
    config = PlaygroundConfig(token=token, enable_live=args.allow_live, max_units=args.max_units)
    uvicorn.run(
        create_app(config), host=args.host, port=args.port, access_log=False, proxy_headers=False
    )


if __name__ == "__main__":
    main()
