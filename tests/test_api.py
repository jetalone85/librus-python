import unittest
from unittest.mock import patch, MagicMock

from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

from librus_python.api import Librus


class TestLibrus(unittest.TestCase):
    @patch('librus_python.api.Librus._prepare_cookies')
    def test_prepare_cookies_with_cookies(self, mock_prepare_cookies):
        librus = Librus()
        cookies = {"test_cookie": "test_value"}
        cookie_jar = RequestsCookieJar()
        cookie_jar.update(cookies)
        mock_prepare_cookies.return_value = cookie_jar

        jar = librus._prepare_cookies(cookies)

        self.assertIsInstance(jar, RequestsCookieJar)

    def test_prepare_cookies_without_cookies(self):
        librus = Librus()
        jar = librus._prepare_cookies(None)

        self.assertIsInstance(jar, RequestsCookieJar)

    @patch('librus_python.api.Librus._prepare_cookies')
    @patch('librus_python.api.Librus._attempt_login')
    def test_authorize(self, mock_attempt_login, mock_prepare_cookies):
        librus = Librus()
        login = "test_login"
        password = "test_password"
        mock_attempt_login.return_value = None
        mock_prepare_cookies.return_value = RequestsCookieJar()

        result = librus.authorize(login, password)

        self.assertIsNone(result)
        mock_attempt_login.assert_called_once_with(login, password)
        mock_prepare_cookies.assert_called()

    @patch('requests.Session')
    def test_make_request_with_parse_html(self, mock_session):
        mock_response = mock_session.return_value.request.return_value
        mock_response.text = "<html></html>"
        librus = Librus()

        result = librus.make_request('get', 'http://example.com', parse_html=True)

        self.assertIsInstance(result, BeautifulSoup)
        mock_session.return_value.request.assert_called_with('get', 'http://example.com', data=None)

    def test_load_document(self):
        librus = Librus()
        html_content = "<html><body>Hello</body></html>"
        soup = librus.load_document(html_content)

        self.assertIsInstance(soup, BeautifulSoup)

    def test_map_table_values(self):
        librus = Librus()
        html_content = "<html><body><table><tr><td>Key</td><td>Value</td></tr></table></body></html>"
        soup = librus.load_document(html_content)
        keys = ["Key"]
        result = librus.map_table_values(soup, keys)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["Key"], "Value")

    @patch('librus_python.api.requests')
    def test_handle_redirects_with_Location(self, mock_requests):
        mock_response = MagicMock(headers={'Location': 'https://example.com/GetFile'})
        librus = Librus()
        librus.session = MagicMock()
        librus.session.get.return_value.content = b'\x50\x4b\x03\x04'

        mock_requests.get.return_value = mock_response
        result = librus._handle_redirects(mock_response)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b'\x50\x4b\x03\x04')
        librus.session.get.assert_called_once_with('https://example.com/GetFile', stream=True)

    @patch('librus_python.api.requests')
    def test_handle_redirects_without_Location(self, mock_requests):
        mock_get = mock_requests.get.return_value
        mock_get.headers = {}
        mock_get.content = b'\x50\x4b\x03\x04'

        librus = Librus()

        result = librus._handle_redirects(mock_get)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
