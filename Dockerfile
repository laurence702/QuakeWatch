# Use an official lightweight Python image
FROM python:3.11-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies that might be needed by Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code and data
COPY src/ ./src/
COPY data/ ./data/

# Expose the port that Streamlit runs on
EXPOSE 8501

# Create a script to run the pipeline and then start the dashboard
# This ensures that when the container starts, it always has the latest data
RUN echo '#!/bin/sh' > ./run.sh && \
    echo 'echo "--- Running Data Pipeline ---"' >> ./run.sh && \
    echo 'python src/ingest_data.py' >> ./run.sh && \
    echo 'python src/process_data.py' >> ./run.sh && \
    echo 'python src/analyze_and_alert.py' >> ./run.sh && \
    echo 'echo "--- Starting Dashboard ---"' >> ./run.sh && \
    echo 'streamlit run src/dashboard.py --server.port 8501 --server.address 0.0.0.0' >> ./run.sh && \
    chmod +x ./run.sh

# The command to run when the container starts
CMD ["./run.sh"]
