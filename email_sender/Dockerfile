# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directory for data persistence with proper permissions
RUN mkdir -p /app/data && chmod 777 /app/data
RUN mkdir -p /app/instance && chmod 777 /app/instance

# Create a non-root user with specific UID/GID
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1001 appuser

# Change ownership of the app directory to appuser
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Run the email sender script
CMD ["python", "-u", "email_sender.py"]