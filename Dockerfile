# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for some Python libs
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy everything from your local folder to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Streamlit uses port 8501 by default
EXPOSE 8501

# Command to run the app, binding to 0.0.0.0 and using Render's dynamic PORT
CMD ["streamlit", "run", "weather.py", "--server.port", "8501", "--server.address", "0.0.0.0"]