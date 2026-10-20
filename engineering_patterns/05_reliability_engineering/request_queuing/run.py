"""Queue bounded work and drain it in FIFO order."""

from applied_ai.reliability import RequestQueue


def main() -> None:
    queue = RequestQueue(max_size=2)
    queue.enqueue("first")
    queue.enqueue("second")
    print(queue.drain(str.upper))
    queue.enqueue("forth")
    print(queue.drain(str.upper))


if __name__ == "__main__":
    main()
