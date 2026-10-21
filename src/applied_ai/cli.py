"""Minimal offline-safe command-line entry point for the SDK."""

from __future__ import annotations

import argparse

from applied_ai.client import AppliedAIClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a provider-neutral Applied AI request")
    parser.add_argument("prompt", help="User prompt to send")
    parser.add_argument(
        "--live", action="store_true", help="Explicitly allow a configured live provider"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    client = AppliedAIClient.from_environment(allow_live=args.live)
    print(client.ask(args.prompt).text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
