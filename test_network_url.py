import unittest
from unittest.mock import patch

from web_server import local_network_url


class LocalNetworkUrlTests(unittest.TestCase):
    @patch("web_server.socket.getaddrinfo", return_value=[(2, 0, 0, "", ("0.0.0.0", 0))])
    @patch("web_server.socket.gethostbyname_ex", return_value=("host", [], ["10.0.0.42"]))
    def test_ignores_unspecified_addresses_and_uses_hostname_fallback(self, _mock_gethostbyname_ex, _mock_getaddrinfo):
        self.assertEqual(local_network_url(), "http://10.0.0.42:8000")

    @patch("web_server.socket.getaddrinfo", side_effect=OSError)
    @patch("web_server.socket.gethostbyname_ex", return_value=("host", [], ["127.0.0.1"]))
    def test_falls_back_to_loopback_when_no_private_address_exists(self, _mock_gethostbyname_ex, _mock_getaddrinfo):
        self.assertEqual(local_network_url(), "http://127.0.0.1:8000")


if __name__ == "__main__":
    unittest.main()
