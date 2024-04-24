# Use the official Python image as the base image
FROM python:3.8-slim-buster

# Set the working directory
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Install lxml
RUN apt-get update && \
    apt-get install -y libxml2 && \
    pip install --no-cache-dir lxml && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Copy the project files to the container
COPY . .

# Command to run the application
CMD ["python", "server.py"]