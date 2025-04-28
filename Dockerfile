# Use a base Python image
FROM python:3.10-alpine3.18

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/py/bin:$PATH"

# Build argument for development mode
ARG DEV=true

# Install system dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev build-base

# Create a virtual environment
# RUN python -m venv /py && /py/bin/pip install --upgrade pip
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \    
    apk add --no-cache postgresql-client && \
    apk add --no-cache --virtual .temp-build-deps \
        build-base postgresql-dev musl-dev

# Copy requirements files and install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN /py/bin/pip install -r /tmp/requirements.txt

# Copy the entire project into the container
COPY . /kinamelnepal_backend

# Set the working directory
WORKDIR /kinamelnepal_backend

# Expose the port for the application
EXPOSE 8000

# Add a non-root user for security
RUN adduser --disabled-password --no-create-home django-user
USER django-user

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
