import argparse
import json
import logging
import os
from librus_python.api import Librus
from librus_python.resources.absence import Absence
from librus_python.resources.grade import Grade
from librus_python.resources.inbox import Inbox


def setup_logging(log_level):
    """
    Configures logging based on the specified log level.
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')


def get_user_credentials():
    """
    Retrieves user credentials from environment variables.
    """
    login = os.getenv("LIBRUS_LOGIN")
    password = os.getenv("LIBRUS_PASSWORD")
    if not login or not password:
        logging.error("Login credentials are not set.")
        return None, None
    return login, password


def authorize_client(librus_client):
    """
    Authorizes the Librus client using provided credentials.
    """
    login, password = get_user_credentials()
    if login and password:
        try:
            cookies = librus_client.authorize(login=login, password=password)
            if cookies:
                logging.info("Authorization successful.")
                return True
        except Exception as e:
            logging.exception("Failed to authorize:")
    return False


def handle_operation(librus_client, resource_cls, method_name, *args):
    """
    Handles operations on different Librus resources.
    """
    try:
        resource = resource_cls(librus_client)
        result = getattr(resource, method_name)(*args)
        logging.info(f"{method_name.replace('_', ' ').capitalize()} executed successfully.")
        logging.info(result)

        print(json.dumps(result, indent=2))
    except Exception as e:
        logging.exception(f"Failed to execute {method_name}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Run Librus client application.")
    parser.add_argument('--log', dest='log_level', default='ERROR',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the logging level')
    parser.add_argument('command', choices=['absences', 'inbox', 'message', 'grades'],
                        help='Specify the operation to perform')
    parser.add_argument('--message_id', type=int, help='Specify the message ID for fetching a specific message')
    args = parser.parse_args()

    setup_logging(args.log_level)

    librus_client = Librus(cookies=None)
    if not authorize_client(librus_client):
        return

    # Command-specific operations
    if args.command == 'absences':
        handle_operation(librus_client, Absence, 'get_absences')
    elif args.command == 'inbox':
        handle_operation(librus_client, Inbox, 'list_inbox', 5)
    elif args.command == 'message' and args.message_id:
        handle_operation(librus_client, Inbox, 'get_message', 5, args.message_id)
    elif args.command == 'grades':
        handle_operation(librus_client, Grade, 'get_grades')


if __name__ == "__main__":
    main()
