"""Command line entry point for the Hello world project."""


def get_message() -> str:
    """Return the greeting displayed by the application."""
    return "Hello, world!"


def main() -> None:
    """Print the greeting to standard output."""
    print(get_message())


if __name__ == "__main__":
    main()
