from unittest.mock import Mock, patch

import pytest
from bs4 import BeautifulSoup

from librus_python.resources import grade


@pytest.fixture
def grade_instance():
    api = Mock()
    return grade.Grade(api)


class TestGrade:
    def test_constructor(self, grade_instance):
        assert isinstance(grade_instance, grade.Grade)

    def test_get_grades(self, grade_instance):
        with patch("librus_python.resources.grade.Grade.parser") as mock_parser:
            grade_instance.api.make_request.return_value = "mock response"
            grade_instance.get_grades()

            grade_instance.api.make_request.assert_called_once_with(
                'GET', "https://synergia.librus.pl/przegladaj_oceny/uczen", parse_html=True)
            mock_parser.assert_called_once_with("mock response")

    def test_parser(self, grade_instance):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert grade_instance.parser(soup) == []

    def test_process_grade(self, grade_instance):
        grade_html = "<a title='Test Title: Value'>5</a>"
        soup = BeautifulSoup(grade_html, "html.parser")
        grade_tag = soup.select_one("a")
        expected = {"value": "5", "info": {"Test Title": "Value"}}

        assert grade_instance.process_grade(grade_tag) == expected

    def test_parse_title(self, grade_instance):
        title = "Key: Value<br />Another Key: Another Value"
        expected = {"Key": "Value", "Another Key": "Another Value"}

        assert grade_instance.parse_title(title) == expected

    def test_parse_semester(self, grade_instance):
        row_html = """
        <tr>
            <td><span class='grade-box'><a title='Test Title: Test Value'>5</a></span></td>
            <td>4.5</td>
            <td>4.0</td>
        </tr>
        """
        soup = BeautifulSoup(row_html, "html.parser")
        cells = soup.select("td")
        start_column = 0
        expected_result = {
            "grades": [{"value": "5", "info": {"Test Title": "Test Value"}}],
            "tempAverage": 4.5,
            "average": 4.0,
        }

        assert grade_instance.parse_semester(cells, start_column) == expected_result
