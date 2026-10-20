"""Decode structured output only when required keys are present."""

from applied_ai.reliability import recover_json_output


def main() -> None:
    print(recover_json_output('{"answer": "42"}', required_keys={"answer"}))


if __name__ == "__main__":
    main()
