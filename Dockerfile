# Use Python 3.10 slim as base image for a smaller footprint
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies required for Poetry
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="${PATH}:/root/.local/bin"

# Copy the entire application
COPY . .

# Configure Poetry to not create a virtual environment inside the Docker container
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only main --no-interaction --no-ansi --no-root

# Expose the Streamlit port
EXPOSE 8501

# Set the entrypoint to run Streamlit
CMD ["poetry", "run", "streamlit", "run", "app.py"]