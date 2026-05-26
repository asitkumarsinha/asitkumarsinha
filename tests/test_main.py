from hello_world.main import get_message


def test_get_message_returns_hello_world() -> None:
    assert get_message() == "Hello, world!"
