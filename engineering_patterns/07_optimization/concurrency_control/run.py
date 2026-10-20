"""Offline concurrency control demonstration."""

import asyncio

from applied_ai.optimization import bounded_map


async def main() -> None:
    print(
        await bounded_map((1, 2), lambda item: asyncio.sleep(0, result=item * 2), max_concurrency=1)
    )


if __name__ == "__main__":
    asyncio.run(main())
