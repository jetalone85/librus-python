import requests
from requests.cookies import RequestsCookieJar
from urllib.parse import urlparse, urljoin
import logging
from bs4 import BeautifulSoup
from librus_python.config import Config


class Librus:
    """
    A class to interact with the Librus Synergia API, managing sessions, authentication,
    and requests to various endpoints.

    Attributes
    ----------
    session : requests.Session
        A session object to manage and persist settings across requests to the API.

    Methods
    -------
    authorize(login, password):
        Authenticate a user using their login credentials and return session cookies.
    make_request(method, api_function, data=None, parse_html=False):
        Send a request to a specific API endpoint and optionally parse the response as HTML.
    get_file(path):
        Retrieve and return content of a file from a specified path or URL.
    load_document(html_content):
        Load and return a BeautifulSoup object from a string of HTML content.
    map_table_values(soup, keys):
        Extract and map values from a table in the HTML to specified keys.
    wait_for_file_ready(key, options, redirect):
        Method stub for implementing asynchronous file readiness checks.
    """

    def __init__(self, cookies=None):
        """
        Initializes the Librus object with optional cookies.

        Parameters
        ----------
        cookies : dict, optional
            A dictionary of cookies to be used for initializing the session (default is None).
        """
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": Config.USER_AGENT})
        self.session.cookies.update(self._prepare_cookies(cookies))

    def _prepare_cookies(self, cookies):
        """
        Prepares and returns a RequestsCookieJar from a dictionary of cookies.

        Parameters
        ----------
        cookies : dict
            A dictionary where keys are cookie names and values are cookie values.

        Returns
        -------
        RequestsCookieJar
            A cookie jar containing all cookies set for the session's domain.
        """
        cookie_jar = RequestsCookieJar()
        if cookies:
            domain = urlparse(Config.BASE_URL).netloc
            for name, value in cookies.items():
                cookie_jar.set(name, value, domain=domain)
        return cookie_jar

    def authorize(self, login, password):
        """
        Attempt to authorize with the Librus Synergia service using the provided credentials.

        Parameters
        ----------
        login : str
            The user's login username.
        password : str
            The user's password.

        Returns
        -------
        dict or None
            A dictionary of session cookies if authentication is successful, otherwise None.
        """
        return self._attempt_login(login, password)

    def _attempt_login(self, login, password):
        """
        Helper method to perform the login action.

        Parameters
        ----------
        login : str
            The user's login username.
        password : str
            The user's password.

        Returns
        -------
        dict or None
            A dictionary of session cookies if the login is successful, otherwise None.
        """
        try:
            response = self._make_request('get', Config.AUTH_URL)
            login_data = {'action': Config.LOGIN_DATA_ACTION, 'login': login, 'pass': password}
            self._make_request('post', Config.LOGIN_URL, login_data)
            response_2fa = self._make_request('get', Config.TWO_FA_URL)
            return response_2fa.cookies.get_dict()
        except Exception as e:
            logging.exception("Error during authorization")
            return None

    def make_request(self, method, api_function, data=None, parse_html=False):
        """
        Generic method to make HTTP requests to the specified API endpoint.

        Parameters
        ----------
        method : str
            The HTTP method to use ('get', 'post', etc.).
        api_function : str
            The specific API function or endpoint to call.
        data : dict, optional
            Data to send with the request (default is None).
        parse_html : bool, optional
            Whether to parse the response text as HTML and return a BeautifulSoup object (default is False).

        Returns
        -------
        Response or BeautifulSoup
            The raw response object if parse_html is False, otherwise a BeautifulSoup object parsed from the response.
        """
        url = urljoin(Config.BASE_URL, api_function)
        response = self._make_request(method, url, data)
        if parse_html:
            return BeautifulSoup(response.text, 'html.parser') if response else None
        return response.json() if response else None

    def _make_request(self, method, url, data=None):
        """
        A private method to encapsulate the logic of making HTTP requests.

        Parameters
        ----------
        method : str
            The HTTP method to use.
        url : str
            The full URL to which the request is sent.
        data : dict, optional
            Any data to send with the request (used in POST requests).

        Returns
        -------
        requests.Response
            The response object returned by the requests library.
        """
        try:
            response = self.session.request(method, url, data=data)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error {e.response.status_code} at {url}: {e.response.text}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        return None

    def get_file(self, path):
        """
        Retrieves a file from a specified path or URL, handling potential redirects.

        Parameters
        ----------
        path : str
            The path or URL from which to fetch the file.

        Returns
        -------
        bytes or None
            The content of the file as bytes if successful, None otherwise.
        """
        url = urljoin(Config.BASE_URL, path) if not path.startswith("https://") else path
        response = self.session.get(url, allow_redirects=False)
        return self._handle_redirects(response)

    def _handle_redirects(self, response):
        """
        Private helper method to handle HTTP redirects when fetching files.

        Parameters
        ----------
        response : requests.Response
            The initial response object from the get_file request.

        Returns
        -------
        bytes or None
            The redirected file content as bytes if successful, None otherwise.
        """
        if 'Location' in response.headers:
            redirect_url = response.headers['Location']
            if "GetFile" in redirect_url:
                return self.session.get(redirect_url, stream=True).content
        return None

    @staticmethod
    def load_document(html_content):
        """
        Loads HTML content into a BeautifulSoup object for parsing.

        Parameters
        ----------
        html_content : str
            A string containing the HTML content to be parsed.

        Returns
        -------
        BeautifulSoup
            A BeautifulSoup object containing the parsed HTML.
        """
        return BeautifulSoup(html_content, 'html.parser')

    @staticmethod
    def map_table_values(soup, keys):
        """
        Maps and returns key-value pairs from table rows within an HTML document.

        Parameters
        ----------
        soup : BeautifulSoup
            A BeautifulSoup object containing the HTML from which to extract table values.
        keys : list of str
            A list of keys corresponding to the table values to extract.

        Returns
        -------
        dict
            A dictionary with keys mapped to corresponding table values.
        """
        rows = soup.find_all('tr')
        values = [row.find_all('td')[1].text.strip() for row in rows if len(row.find_all('td')) > 1]
        return dict(zip(keys, values))

    def wait_for_file_ready(self, key, options, redirect):
        """
        Waits for a file to be ready for download, potentially handling asynchronous operations.

        Parameters
        ----------
        key : str
            A unique key to identify the file or process.
        options : dict
            Options and parameters to control the file readiness check.
        redirect : bool
            Whether to follow redirects while checking file readiness.

        This method is a placeholder and needs to be implemented based on specific requirements.
        """
        pass
