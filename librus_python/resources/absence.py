import re
import logging


class Absence:
    """
    The Absence class is responsible for fetching and processing absence data from an API.

    Attributes:
        api (object): An instance of the API class used to make requests.
    """

    def __init__(self, api):
        """
        The constructor for the Absence class.

        Parameters:
            api (object): An instance of the API class.
        """
        self.api = api

    def get_absence(self, id):
        """
        Fetches and processes the absence data for a specific ID.

        Parameters:
            id (int): The ID of the absence to fetch.

        Returns:
            dict: A dictionary containing the absence data, or None if the request fails.
        """
        logging.debug(f"Fetching absence details for ID: {id}")
        soup = self.api.make_request('GET', f"przegladaj_nb/szczegoly/{id}", parse_html=True)
        if not soup:
            logging.error(f"Failed to retrieve absence details for ID: {id}")
            return None

        keys = ["type", "category", "date", "subject", "lesson_hour", "teacher", "trip", "added_by"]
        data = self.table_mapper(soup, "table.decorated tbody", keys)

        if any(value is None for value in data.values()):
            logging.warning(f"Missing data for some fields in absence ID: {id}")
            keys.remove("category")  # Assume 'category' might be missing in some cases.
            data = self.table_mapper(soup, "table.decorated tbody", keys)

        data['trip'] = self.make_boolean(data.get('trip', 'no'))
        logging.info(f"Processed absence data for ID: {id}: {data}")
        return data

    def get_absences(self):
        """
        Fetches and processes all absences.

        Returns:
            list: A list of dictionaries containing the absence data, or an empty list if the request fails.
        """
        logging.debug("Fetching all absences.")
        soup = self.api.make_request('GET', "przegladaj_nb/uczen", parse_html=True)
        if not soup:
            logging.error("Failed to retrieve absences.")
            return []

        absences = []
        semester_size = -1
        for i, row in enumerate(soup.select("table.center.big.decorated tr[class*='line']")):
            if self.is_semester_header(row):
                semester_size = i  # Track the semester separation.
                continue

            try:
                absence_data = self.parse_absence_row(row)
                if absence_data:
                    absences.append(absence_data)
            except IndexError as e:
                logging.error(f"IndexError while processing row {i}: {e}")
                continue  # Continue processing other rows even if one fails
        logging.info(f"Retrieved {len(absences)} absences.")
        return absences

    @staticmethod
    def is_semester_header(row):
        """
        Checks if a row is a semester header.

        Parameters:
            row (bs4.element.Tag): A BeautifulSoup Tag object representing a row in the table.

        Returns:
            bool: True if the row is a semester header, False otherwise.
        """
        semester_row = row.select(".center.bolded")
        is_header = bool(semester_row) and semester_row[0].text.strip() == "Okres 1"
        logging.debug(f"Checking if row is a semester header: {is_header}")
        return is_header

    def parse_absence_row(self, row):
        """
        Parses a row from the absences table and extracts the absence data.

        Parameters:
            row (bs4.element.Tag): A BeautifulSoup Tag object representing a row in the table.

        Returns:
            dict: A dictionary containing the absence data, or None if the row does not contain valid data.
        """
        cols = row.find_all("td")
        if len(cols) < 6:
            logging.warning(f"Skipping row with insufficient data: expected at least 6 columns, found {len(cols)}")
            return None

        date = cols[0].text.strip()
        if not date:
            logging.debug("Skipping a row without a date.")
            return None

        absence_data = {
            'date': date,
            'table': self.extract_absences(cols[1]),
            'info': [col.text.strip() for col in cols[-5:]]
        }
        return absence_data

    @staticmethod
    def extract_absences(column):
        """
        Extracts absence details from a column in the table.

        Parameters:
            column (bs4.element.Tag): A BeautifulSoup Tag object representing a column in the table.

        Returns:
            list: A list of dictionaries containing the absence details.
        """
        table = []
        for link in column.find_all('a'):
            onclick_attr = link.get('onclick', '')
            logging.debug(f"Processing onclick attribute: {onclick_attr}")
            id_match = re.search(r'/szczegoly/(\d+)', onclick_attr)
            if id_match:
                table.append({
                    'type': link.text.strip(),
                    'id': int(id_match.group(1))
                })
        logging.debug(f"Extracted absence details from table: {table}")
        return table

    @staticmethod
    def table_mapper(soup, selector, keys):
        """
        Maps data from a table to a dictionary.

        Parameters:
            soup (bs4.BeautifulSoup): A BeautifulSoup object containing the HTML of the page.
            selector (str): A CSS selector to select the table.
            keys (list): A list of keys to use for the dictionary.

        Returns:
            dict: A dictionary containing the table data.
        """
        table = soup.select_one(selector)
        if not table:
            logging.warning(f"Table not found using selector: {selector}")
            return {key: None for key in keys}

        result = {}
        for row, key in zip(table.find_all('tr'), keys):
            cells = row.find_all('td')
            result[key] = cells[1].text.strip() if len(cells) > 1 else None
        logging.debug(f"Mapped table data: {result}")
        return result

    @staticmethod
    def make_boolean(value):
        """
        Converts a value to a boolean.

        Parameters:
            value (str): The value to convert.

        Returns:
            bool: The boolean representation of the value.
        """
        result = value.lower() in ['tak', 'yes'] if isinstance(value, str) else bool(value)
        logging.debug(f"Converted '{value}' to boolean: {result}")
        return result
