# Use an official lightweight Python image
FROM python:3.11-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies that might be needed by Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY src/ ./src/

# Copy the run script and make it executable
COPY run.sh .
RUN chmod +x ./run.sh

# Expose the port that Streamlit runs on
EXPOSE 8501


