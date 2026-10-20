"""Offline execution failure recovery demonstration."""

from applied_ai.reasoning import recover_execution


def main() -> None:
    print(
        recover_execution(lambda: (_ for _ in ()).throw(RuntimeError("fail")), lambda: "fallback")
    )


if __name__ == "__main__":
    main()
