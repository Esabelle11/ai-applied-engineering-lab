"""Offline sandboxed python execution demonstration."""

from applied_ai.execution import DockerPythonSandbox


def main() -> None:
    print(
        "DockerPythonSandbox is the isolated execution boundary; configure Docker before live execution."
    )
    print(DockerPythonSandbox.__name__)


if __name__ == "__main__":
    main()
