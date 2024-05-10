import argparse
import logging
import os
from librus_python.api import Librus
from librus_python.resources.absence import Absence
from librus_python.resources.grade import Grade
from librus_python.resources.inbox import Inbox


def setup_logging():
    """
    Configures logging based on command line arguments.

    This function parses command line arguments to set the logging level
    for the application. Valid log levels include DEBUG, INFO, WARNING, ERROR, and CRITICAL.
    """
    parser = argparse.ArgumentParser(description="Run Librus client application.")
    parser.add_argument('--log', dest='log_level', default='INFO', choices=[
        'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the logging level')

    args = parser.parse_args()

    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {args.log_level}')

    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    """
    Main function that orchestrates the flow of the Librus client application.

    This function handles:
    - Setting up logging.
    - Authorizing the user.
    - Retrieving absences, inbox messages, and grades.
    """
    setup_logging()

    # Retrieve credentials securely from environment variables
    login = os.getenv("LIBRUS_LOGIN")
    password = os.getenv("LIBRUS_PASSWORD")

    if not login or not password:
        logging.error("Login credentials are not set.")
        return

    # Initialize the Librus client with no predefined cookies
    librus_client = Librus(cookies=None)

    # Attempt to authorize with the Librus client
    try:
        cookies = librus_client.authorize(login=login, password=password)
        if cookies:
            logging.info("Authorization successful.")
        else:
            logging.error("Authorization failed.")
            return
    except Exception as e:
        logging.exception("Failed to authorize:")
        return

    # Handle operations for different resources
    operations = [
        ("absences", Absence, "get_absences"),
        ("inbox", Inbox, "list_inbox", 5),
        ("specific message", Inbox, "get_message", 5, 12345678),
        ("grades", Grade, "get_grades")
    ]

    for name, resource, method, *args in operations:
        try:
            handler = resource(librus_client)
            result = getattr(handler, method)(*args)
            logging.info(f"{name.capitalize()} retrieved successfully:")
            logging.info(result)
        except Exception as e:
            logging.exception(f"Failed to retrieve {name}: {e}")


if __name__ == "__main__":
    main()
