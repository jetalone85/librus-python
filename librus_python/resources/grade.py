import logging


class Grade:
    """
    The Grade class is responsible for fetching and processing grade data from an API.

    Attributes:
        api (object): An instance of the API class used to make requests.
    """

    def __init__(self, api):
        """
        The constructor for the Grade class.

        Parameters:
            api (object): An instance of the API class.
        """
        self.api = api
        logging.debug("Grade class instantiated with API.")

    def get_grades(self):
        """
        Fetches and processes all grades.

        Returns:
            list: A list of dictionaries containing the grade data, or an empty list if the request fails.
        """
        logging.info("Fetching all grades.")
        response = self.api.make_request('GET', "https://synergia.librus.pl/przegladaj_oceny/uczen", parse_html=True)
        if not response:
            logging.error("Failed to retrieve grades.")
            return []
        return self.parser(response)

    def parser(self, soup):
        """
        Parses the HTML response and extracts the grade data.

        Parameters:
            soup (bs4.BeautifulSoup): A BeautifulSoup object containing the HTML of the page.

        Returns:
            list: A list of dictionaries containing the grade data.
        """
        rows = soup.select("table.decorated.stretch > tbody > tr[class^='line']")
        grades_info = []
        for row in rows:
            subject_cell = row.select_one("td:nth-of-type(2)")
            if subject_cell is None:
                logging.warning("No subject cell found in row, skipping row.")
                continue
            subject = subject_cell.text.strip()
            grade_spans = row.select("span.grade-box a")
            grades = [self.process_grade(grade) for grade in grade_spans if grade]
            if grades:
                grades_info.append({
                    "subject": subject,
                    "grades": grades
                })
        return grades_info

    def process_grade(self, grade):
        """
        Processes a grade element and extracts the grade data.

        Parameters:
            grade (bs4.element.Tag): A BeautifulSoup Tag object representing a grade element.

        Returns:
            dict: A dictionary containing the grade data.
        """
        grade_details = {
            "value": grade.text.strip(),
            "info": self.parse_title(grade['title'])
        }
        logging.debug(f"Processed grade: {grade_details}")
        return grade_details

    @staticmethod
    def parse_title(title):
        """
        Extracts details from the title attribute using key-value parsing.

        Parameters:
            title (str): The title attribute of a grade element.

        Returns:
            dict: A dictionary containing the parsed title data.
        """
        details = {}
        parts = title.split("<br />")
        for part in parts:
            key, value = part.split(":", 1)
            details[key.strip()] = value.strip()
            logging.debug(f"Parsed title part: {key.strip()}: {value.strip()}")
        return details

    def parse_semester(self, cells, start_column):
        """
        Parses a semester cell and extracts the semester data.

        Parameters:
            cells (list): A list of BeautifulSoup Tag objects representing the cells in a row.
            start_column (int): The index of the cell to start parsing from.

        Returns:
            dict: A dictionary containing the semester data.
        """
        grades = [self.process_grade(a) for a in cells[start_column].select("span.grade-box a")]
        semester_info = {
            "grades": grades,
            "tempAverage": float(cells[start_column + 1].text.strip()),
            "average": float(cells[start_column + 2].text.strip())
        }
        logging.info(f"Semester parsed with temporary and final averages.")
        return semester_info
