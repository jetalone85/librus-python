# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV LIBRUS_LOGIN=your_login
ENV LIBRUS_PASSWORD=your_password

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the application code into the container
COPY . /app

# Set the entrypoint to poetry run python main.py
ENTRYPOINT ["poetry", "run", "python", "main.py"]

# Default command arguments
CMD ["--help"]
