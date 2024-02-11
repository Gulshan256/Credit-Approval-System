# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/
# Run migrations
RUN python manage.py makemigrations
RUN python manage.py migrate


# Run import_data.py script
# RUN python import_data.py

# Expose port 8000 to the outside world
EXPOSE 8000

# Define the command to run your server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
