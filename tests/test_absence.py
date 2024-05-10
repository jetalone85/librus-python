import unittest
from unittest.mock import MagicMock

from bs4 import BeautifulSoup

from librus_python.resources.absence import Absence


class TestAbsence(unittest.TestCase):
    def setUp(self):
        self.api_mock = MagicMock()
        self.absence = Absence(self.api_mock)

    def test_get_absence(self):
        html_data = "<html><body><table><tr><td>Key1</td><td>value1</td><td>Key2</td><td>value2</td><td>trip</td><td>yes</td></tr></table></body></html>"
        soup = BeautifulSoup(html_data, 'html.parser')
        self.api_mock.make_request.return_value = soup
        self.absence.table_mapper = MagicMock(return_value={"key1": "value1", "key2": "value2", "trip": "yes"})
        self.absence.make_boolean = MagicMock(return_value=True)

        result = self.absence.get_absence(123)
        expected_result = {"key1": "value1", "key2": "value2", "trip": True}

        self.api_mock.make_request.assert_called_with('GET', "przegladaj_nb/szczegoly/123", parse_html=True)
        self.assertEqual(result, expected_result)

    def test_get_absences(self):
        html_data = "<html><body><table class='center big decorated'><tr class='line'><td>Key</td><td>value</td></tr></table></body></html>"
        soup = BeautifulSoup(html_data, 'html.parser')
        self.api_mock.make_request.return_value = soup
        self.absence.is_semester_header = MagicMock(return_value=False)
        self.absence.parse_absence_row = MagicMock(return_value={"key": "value"})

        result = self.absence.get_absences()
        expected_result = [{"key": "value"}]

        self.api_mock.make_request.assert_called_with('GET', "przegladaj_nb/uczen", parse_html=True)
        self.assertEqual(result, expected_result)

    def test_is_semester_header(self):
        row_mock = MagicMock()
        row_mock.select.return_value = [MagicMock(text="Okres 1")]

        result = self.absence.is_semester_header(row_mock)

        row_mock.select.assert_called_with(".center.bolded")
        self.assertTrue(result)

    def test_parse_absence_row(self):
        row_mock = MagicMock()
        row_mock.find_all.return_value = [MagicMock(text="test_data") for _ in range(6)]
        self.absence.extract_absences = MagicMock(return_value="absences_data")

        result = self.absence.parse_absence_row(row_mock)
        expected_result = {'date': 'test_data', 'table': 'absences_data', 'info': ['test_data'] * 5}

        self.assertEqual(result, expected_result)

    def test_extract_absences(self):
        column_mock = MagicMock()
        link_mock = MagicMock()
        link_mock.get.return_value = '/szczegoly/123'
        link_mock.text = "test_data"
        column_mock.find_all.return_value = [link_mock]

        result = self.absence.extract_absences(column_mock)
        expected_result = [{'type': 'test_data', 'id': 123}]

        link_mock.get.assert_called_with('onclick', '')
        self.assertEqual(result, expected_result)

    def test_table_mapper(self):
        soup_mock = MagicMock()
        table_mock = MagicMock()
        row_mock_1 = MagicMock()
        row_mock_2 = MagicMock()
        cell_mock_1 = MagicMock(text="test_data_1")
        cell_mock_2 = MagicMock(text="test_data_2")

        row_mock_1.find_all.return_value = [MagicMock(), cell_mock_1]
        row_mock_2.find_all.return_value = [MagicMock(), cell_mock_2]
        table_mock.find_all.return_value = [row_mock_1, row_mock_2]
        soup_mock.select_one.return_value = table_mock

        keys = ["key1", "key2"]
        result = Absence.table_mapper(soup_mock, "selector", keys)
        expected_result = {'key1': 'test_data_1', 'key2': 'test_data_2'}

        self.assertEqual(result, expected_result)

        row_mock_3 = MagicMock()
        row_mock_3.find_all.return_value = [MagicMock()]
        table_mock.find_all.return_value.append(row_mock_3)
        keys.append('key3')

        result_with_key3 = Absence.table_mapper(soup_mock, "selector", keys)
        expected_result_with_key3 = {'key1': 'test_data_1', 'key2': 'test_data_2', 'key3': None}
        self.assertEqual(result_with_key3, expected_result_with_key3)

    def test_make_boolean(self):
        result = self.absence.make_boolean("Yes")
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
