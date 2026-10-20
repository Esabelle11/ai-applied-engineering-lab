"""Accept only a declared set of output labels."""

from applied_ai.reliability import validate_text_output


def main() -> None:
    print(validate_text_output("positive", allowed={"positive", "negative"}))


if __name__ == "__main__":
    main()
