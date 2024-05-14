# Stage for installing requirements
FROM python:3.12-slim as requirements-stage

# Set the working directory for this stage
WORKDIR /tmp

# Install Poetry package manager
RUN pip install poetry

# Copy the poetry configuration files to the temporary directory
COPY ./pyproject.toml ./poetry.lock* /tmp/

# Export the dependencies to a requirements.txt file without including hash values
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Final stage for running the application
FROM python:3.12-slim

# Set the working directory for this stage
WORKDIR /app

# Copy the requirements.txt file from the requirements-stage to the current directory
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

# Install the dependencies from the requirements.txt file
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy rest of the code
COPY . .

# Remove venv directory
RUN rm -rf venv
