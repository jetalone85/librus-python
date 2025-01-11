# Librus Client Application

This repository houses the Librus Client Application, a Python tool designed to interact with the Librus Synergia API.
It enables users to authenticate and fetch details such as absences, grades, and messages from their Librus accounts.

## Features

- **Authentication**: Secure login using user credentials stored in environment variables.
- **Data Retrieval**: Ability to fetch absences, grades, and inbox messages via CLI.
- **Configurable Logging**: Logging setup that can be adjusted via command-line arguments.

## Prerequisites

Ensure you have Python 3.11+ and Poetry installed on your machine to handle dependencies and run the project.

## Installation

Follow these steps to get your development environment set up:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/librus-client.git
   cd librus-client
   ```
2. **Install Dependencies**:
   Using Poetry, install the dependencies as follows:

```bash
poetry install
```

## Configuration

Set up the necessary environment variables in your system:

```text
LIBRUS_LOGIN: Your Librus Synergia login username.
LIBRUS_PASSWORD: Your Librus Synergia password.
```

For Unix-based systems, you can set these variables like this:

```bash
export LIBRUS_LOGIN='your_login'
export LIBRUS_PASSWORD='your_password'
```

For Windows systems, use:

```cmd
set LIBRUS_LOGIN=your_login
set LIBRUS_PASSWORD=your_password
```

## Usage

To run the application, use Poetry to handle the environment:

```bash
poetry run python main.py
```

You can also specify the logging level with the `--log` argument. Available levels
are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`:

```bash
poetry run python main.py --log LEVEL --command COMMAND
```

Replace `LEVEL` with your preferred logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) and `COMMAND` with
one of the supported operations (absences, inbox, message, grades). If querying a specific message,
include `--message_id ID`.


## Docker

To run the Librus Client Application using Docker, follow these steps:

### Build the Docker Image

1. **Build the Docker Image**:
   Navigate to the project directory and build the Docker image using the following command:

   ```bash
   docker build -t librus-client .
   ```

### Run the Docker Container

2. **Run the Docker Container**:
   Use the following command to run the Docker container, passing the necessary environment variables and command arguments:

   ```bash
   docker run -e LIBRUS_LOGIN='your_login' -e LIBRUS_PASSWORD='your_password' librus-client --log LEVEL --command COMMAND
   ```

   Replace `your_login` and `your_password` with your actual Librus credentials. Replace `LEVEL` with your preferred logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) and `COMMAND` with one of the supported operations (`absences`, `inbox`, `message`, `grades`). If querying a specific message, include `--message_id ID`.

### Example

To run the application with `INFO` logging level and fetch absences, use:

```bash
docker run -e LIBRUS_LOGIN='your_login' -e LIBRUS_PASSWORD='your_password' librus-client --log INFO --command absences
```

### Notes

- Ensure that Docker is installed and running on your machine.
- The Dockerfile is configured to use the official Python 3.11 slim image and installs dependencies using Poetry.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
