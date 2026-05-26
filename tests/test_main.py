import unittest

from hello_world.main import get_message


class GetMessageTest(unittest.TestCase):
    def test_get_message_returns_hello_world(self) -> None:
        self.assertEqual(get_message(), "Hello, world!")


if __name__ == "__main__":
    unittest.main()
