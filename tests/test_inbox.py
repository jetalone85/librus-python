from unittest.mock import MagicMock

import pytest
from bs4 import BeautifulSoup

from librus_python.resources.inbox import Inbox


@pytest.fixture
def inbox():
    api = MagicMock()
    return Inbox(api)


class TestInbox:

    def test_get_confirm_message(self, inbox):
        inbox.api.make_request.return_value = BeautifulSoup(
            '<html><div class="green container">Confirmation</div></html>', 'html.parser')
        assert inbox._get_confirm_message(inbox.api.make_request()) == "Confirmation"

        with pytest.raises(Exception):
            inbox.api.make_request.return_value = BeautifulSoup('<html></html>', 'html.parser')
            inbox._get_confirm_message(inbox.api.make_request())

    def test_get_message(self, inbox):
        inbox.api.make_request.return_value = BeautifulSoup('<html><div></div></html>', 'html.parser')
        with pytest.raises(ValueError):
            inbox.get_message(1, 1)

    def test_remove_message(self, inbox):
        inbox.api.make_request.return_value = BeautifulSoup(
            '<html><div class="green container">Confirmation</div></html>', 'html.parser')
        assert inbox.remove_message(1) == "Confirmation"

    def test_send_message(self, inbox):
        inbox.api.make_request.return_value = BeautifulSoup(
            '<html><div class="green container">Confirmation</div></html>', 'html.parser')
        assert inbox.send_message(1, "Test", "Test") == "Confirmation"

    def test_list_receivers(self, inbox):
        inbox.api.make_request.return_value = BeautifulSoup('<html><div></div></html>', 'html.parser')
        assert inbox.list_receivers(1) == []

    def test_list_inbox(self, inbox):
        inbox.api.make_request.return_value = BeautifulSoup('<html><div></div></html>', 'html.parser')
        assert inbox.list_inbox(1) == []

    def test_list_announcements(self, inbox):
        inbox.api.make_request.return_value = BeautifulSoup('<html><div></div></html>', 'html.parser')
        assert inbox.list_announcements() == []
